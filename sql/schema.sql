CREATE TABLE teams(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(140) NOT NULL,
    abbr VARCHAR(5) NOT NULL
);

CREATE TABLE divisions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR (140) NOT NULL
);

CREATE TABLE season_results(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result VARCHAR(40) NOT NULL
);

CREATE TABLE postseasons(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    team INTEGER,
    wins INTEGER,
    losses INTEGER,
    gp INTEGER,
    abs INTEGER,
    runs INTEGER,
    hits INTEGER,
    doubles INTEGER,
    triples INTEGER,
    homeruns INTEGER,
    rbis INTEGER,
    tb INTEGER,
    bb INTEGER,
    so INTEGER,
    sb INTEGER,
    avg FLOAT,
    obp FLOAT,
    slg FLOAT,
    ops FLOAT,
    era FLOAT,
    sv INTEGER,
    cg INTEGER,
    sho INTEGER,
    qs INTEGER,
    ip FLOAT,
    hits_allowed INTEGER,
    er INTEGER,
    homeruns_allowed INTEGER,
    walks_allowed INTEGER,
    ks INTEGER,
    opponent_avg FLOAT,
    whip FLOAT,
    FOREIGN KEY (team)
        REFERENCES teams (id)
        ON DELETE CASCADE
);

CREATE TABLE seasons(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    team INTEGER,
    division INTEGER,
    division_rank INTEGER,
    season_result INTEGER,
    wins INTEGER,
    losses INTEGER,
    home_wins INTEGER,
    home_losses INTEGER,
    run_diff INTEGER,
    gp INTEGER,
    abs INTEGER,
    runs INTEGER,
    hits INTEGER,
    doubles INTEGER,
    triples INTEGER,
    homeruns INTEGER,
    rbis INTEGER,
    tb INTEGER,
    bb INTEGER,
    so INTEGER,
    sb INTEGER,
    avg FLOAT,
    obp FLOAT,
    slg FLOAT,
    ops FLOAT,
    lob INTEGER,
    ra INTEGER,
    era FLOAT,
    sv INTEGER,
    cg INTEGER,
    sho INTEGER,
    qs INTEGER,
    ip FLOAT,
    hits_allowed INTEGER,
    er INTEGER,
    homeruns_allowed INTEGER,
    walks_allowed INTEGER,
    ks INTEGER,
    opponent_avg FLOAT,
    whip FLOAT,
    FOREIGN KEY (team)
        REFERENCES teams (id)
        ON DELETE CASCADE,
    FOREIGN KEY (division)
        REFERENCES divisions (id)
        ON DELETE CASCADE
    FOREIGN KEY (season_result)
        REFERENCES season_results (id)
        ON DELETE CASCADE
);

CREATE TABLE bullpens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    team INTEGER,
    wins INTEGER,
    losses INTEGER,
    sv INTEGER,
    ip FLOAT,
    kp9 FLOAT,
    bbp9 FLOAT,
    hrp9 FLOAT,
    babip FLOAT,
    lobp FLOAT,
    gbp FLOAT,
    hrpfb FLOAT,
    vfa FLOAT,
    era FLOAT,
    fip FLOAT,
    xfip FLOAT,
    war FLOAT,
    FOREIGN KEY (team)
        REFERENCES teams (id)
);

CREATE TABLE payrolls (
    year INTEGER,
    team INTEGER,
    total_payroll FLOAT,
    bullpen_payroll FLOAT,
    sp_payroll FLOAT,
    PRIMARY KEY (year, team),
    FOREIGN KEY (team)
        REFERENCES teams (id)
);
