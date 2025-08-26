CREATE TABLE session (
  id bigint NOT NULL COMMENT 'id',
  subject varchar(200) COMMENT '本次会话的主题',
  created_at datetime COMMENT '创建时间',
  updated_at datetime COMMENT '更新时间',
  primary key (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话';

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
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='记忆';

CREATE TABLE preference (
  id bigint NOT NULL COMMENT 'id',
  content varchar(1000) COMMENT '偏好内容',
  session_id bigint NOT NULL COMMENT '会话id',
  user_id bigint NOT NULL COMMENT '用户id',
  time datetime COMMENT '发生的时间',
  updated_at datetime COMMENT '更新时间',
  created_at datetime COMMENT '创建时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='偏好';

CREATE TABLE audio (
  id bigint NOT NULL COMMENT 'id',
  oss_url varchar(1000) COMMENT '音频oss地址',
  session_id bigint NOT NULL COMMENT '会话id',
  user_id bigint NOT NULL COMMENT '用户id',
  updated_at datetime COMMENT '更新时间',
  created_at datetime COMMENT '创建时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='音频';

CREATE TABLE picture (
  id bigint NOT NULL COMMENT 'id',
  oss_url varchar(1000) COMMENT '画面oss地址',
  session_id bigint NOT NULL COMMENT '会话id',
  user_id bigint NOT NULL COMMENT '用户id',
  updated_at datetime COMMENT '更新时间',
  created_at datetime COMMENT '创建时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='画面';


CREATE TABLE video (
  id bigint NOT NULL COMMENT 'id',
  oss_url varchar(1000) COMMENT '视频oss地址',
  session_id bigint NOT NULL COMMENT '会话id',
  user_id bigint NOT NULL COMMENT '用户id',
  updated_at datetime COMMENT '更新时间',
  created_at datetime COMMENT '创建时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='视频';

CREATE TABLE user (
  id bigint NOT NULL COMMENT 'id',
  name varchar(1000) COMMENT '用户姓名',
  updated_at datetime COMMENT '更新时间',
  created_at datetime COMMENT '创建时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';


CREATE TABLE user_chat (
  id bigint NOT NULL COMMENT 'id',
  user_id varchar(1000) COMMENT '用户id',
  chat_id bigint NOT NULL COMMENT '聊天记录id',
  face_id bigint COMMENT '人脸id',
  voice_id bigint COMMENT '声纹id',
  updated_at datetime COMMENT '更新时间',
  created_at datetime COMMENT '创建时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户和聊天记录中间表';


CREATE TABLE face (
  id bigint NOT NULL COMMENT 'id',
  user_id bigint NOT NULL COMMENT 'user_id',
  oss_url varchar(1000) COMMENT '人脸oss地址',
  facial_feature varchar(1000) COMMENT '人脸唯一标识',
  updated_at datetime COMMENT '更新时间',
  created_at datetime COMMENT '创建时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人脸';

CREATE TABLE voice (
  id bigint NOT NULL COMMENT 'id',
  oss_url varchar(1000) COMMENT '声音oss地址',
  voiceprint varchar(1000) COMMENT '声音oss地址',
  updated_at datetime COMMENT '更新时间',
  created_at datetime COMMENT '创建时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='声纹';
