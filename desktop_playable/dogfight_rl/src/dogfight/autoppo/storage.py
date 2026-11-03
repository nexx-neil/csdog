"""SQLite is authoritative; filesystem status files are replaceable projections."""
from pathlib import Path
from contextlib import contextmanager
import json,sqlite3,time,uuid,os

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)

def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with tmp.open('w') as f:
            json.dump(value,f,indent=2,allow_nan=False);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
        fd=os.open(path.parent,os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        if tmp.exists():tmp.unlink()

class Store:
    def __init__(self,base):
        self.base=Path(base);self.base.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(self.base/'experiments.sqlite',timeout=30,isolation_level=None)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('PRAGMA foreign_keys=ON');self.db.execute('PRAGMA busy_timeout=30000')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS trials(
          id TEXT PRIMARY KEY,hash TEXT UNIQUE NOT NULL,config TEXT NOT NULL,
          generation INTEGER NOT NULL,stage INTEGER NOT NULL,rung INTEGER DEFAULT 0,
          target INTEGER NOT NULL,progress INTEGER DEFAULT 0,status TEXT DEFAULT 'QUEUED',
          source TEXT,checkpoint TEXT,metrics TEXT,score REAL,diagnosis TEXT,
          retries INTEGER DEFAULT 0,created REAL NOT NULL,updated REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS attempts(
          id TEXT PRIMARY KEY,trial_id TEXT NOT NULL REFERENCES trials(id),
          start_progress INTEGER NOT NULL,observed_updates INTEGER DEFAULT 0,
          pid INTEGER,start REAL NOT NULL,end REAL,status TEXT NOT NULL,
          checkpoint TEXT,wall_seconds REAL DEFAULT 0,environment_steps INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS evaluations(
          id TEXT PRIMARY KEY,trial_id TEXT REFERENCES trials(id),attempt_id TEXT,
          progress INTEGER NOT NULL,protocol TEXT NOT NULL,full INTEGER NOT NULL,
          seeds TEXT NOT NULL,panel_path TEXT NOT NULL,metrics TEXT NOT NULL,created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS checkpoints(
          id TEXT PRIMARY KEY,path TEXT UNIQUE NOT NULL,sha256 TEXT NOT NULL,
          trial_id TEXT,metadata TEXT NOT NULL,metrics TEXT NOT NULL,created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS bank_names(name TEXT PRIMARY KEY,
          checkpoint_id TEXT REFERENCES checkpoints(id));
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,
          time REAL NOT NULL,kind TEXT NOT NULL,trial_id TEXT,data TEXT NOT NULL);
        ''')
    def rows(self,sql,args=()):return [dict(r) for r in self.db.execute(sql,args)]
    def get(self,key,default=None):
        r=self.db.execute('SELECT value FROM meta WHERE key=?',(key,)).fetchone()
        return json.loads(r[0]) if r else default
    def set(self,key,value):self.db.execute('INSERT INTO meta VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,canonical(value)))
    def event(self,kind,trial=None,**data):
        self.db.execute('INSERT INTO events(time,kind,trial_id,data) VALUES(?,?,?,?)',(time.time(),kind,trial,canonical(data)))
    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:yield;self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
    def add_trial(self,config,generation,stage,target,source,digest):
        trial='trial_'+uuid.uuid4().hex[:12];now=time.time()
        with self.transaction():
            try:self.db.execute('INSERT INTO trials(id,hash,config,generation,stage,target,source,created,updated) VALUES(?,?,?,?,?,?,?,?,?)',
                                (trial,digest,canonical(config),generation,stage,target,str(source) if source else None,now,now))
            except sqlite3.IntegrityError:return None
            self.event('CANDIDATE_GENERATED',trial,config=config,target=target,source=str(source))
        (self.base/'trials'/trial).mkdir(parents=True)
        atomic_json(self.base/'trials'/trial/'config.json',config)
        return trial
    def claim(self):
        with self.transaction():
            row=self.db.execute("SELECT * FROM trials WHERE status='QUEUED' ORDER BY generation,rung,created LIMIT 1").fetchone()
            if row is None:return None
            trial=dict(row);attempt='attempt_'+uuid.uuid4().hex[:12]
            self.db.execute("UPDATE trials SET status='RUNNING',updated=? WHERE id=?",(time.time(),trial['id']))
            self.db.execute("INSERT INTO attempts(id,trial_id,start_progress,start,status) VALUES(?,?,?,?,'RUNNING')",(attempt,trial['id'],trial['progress'],time.time()))
            self.event('TRIAL_CLAIMED',trial['id'],attempt=attempt)
        return trial,attempt
    def repair_orphans(self):
        # Caller must hold manager lock, inherited by every worker. Holding it
        # proves no worker of a previous manager can still be alive.
        with self.transaction():
            self.db.execute("UPDATE attempts SET status='CRASHED',end=? WHERE status='RUNNING'",(time.time(),))
            self.db.execute("UPDATE trials SET status=CASE WHEN retries<2 THEN 'QUEUED' ELSE 'FAILED' END,retries=retries+1,diagnosis='PROCESS_EXIT' WHERE status='RUNNING'")
            self.event('ORPHAN_RECOVERY')
    def close(self):self.db.close()
