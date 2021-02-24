from app import db

# 中间表 工作班成员与工作票号 多对多关系
member_gzp = db.Table("member_gzp",
                      db.Column("member_id", db.Integer, db.ForeignKey("users.id")),
                      db.Column("gzp_id", db.Integer, db.ForeignKey("gzps.id"))
                      )

# 中间表 一台风机对应多张工作票，一张工作票也可以有多台风机
wt_gzp = db.Table("wt_gzp",
                  db.Column("wt_id", db.Integer, db.ForeignKey("wts.id")),
                  db.Column("gzp_id", db.Integer, db.ForeignKey("gzps.id"))
                  )

# 中间表 工作任务统计与维护单 多对多关系
statistics_wtm = db.Table('statistics_wtm',
                          db.Column("statistics_id", db.Integer, db.ForeignKey('statistics.id')),
                          db.Column('wtm_id', db.Integer, db.ForeignKey('wtms.id'))
                          )
