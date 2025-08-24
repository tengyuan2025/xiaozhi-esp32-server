-- 系统用户
CREATE TABLE session (
  id bigint NOT NULL COMMENT 'id',
  subject varchar(200) COMMENT '本次会话的主题',
  created_at datetime COMMENT '创建时间',
  updated_at datetime COMMENT '更新时间',
  primary key (id),
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话';

-- 系统用户Token
CREATE TABLE memory (
  id bigint NOT NULL COMMENT 'id',
  session_id bigint NOT NULL COMMENT '会话id',
  user_id bigint NOT NULL COMMENT '用户id',
  event varchar(1000)  COMMENT '事件',
  time datetime COMMENT '事件发生的时间',
  knowledge varchar(1000) COMMENT '知识',
  skill varchar(1000) COMMENT '技能',
  updated_at datetime COMMENT '更新时间',
  created_at datetime COMMENT '创建时间',
  PRIMARY KEY (id),
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='记忆';

