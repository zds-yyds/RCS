/*
 Navicat Premium Data Transfer

 Source Server         : Mysql57
 Source Server Type    : MySQL
 Source Server Version : 50744
 Source Host           : localhost:3306
 Source Schema         : test_rcs

 Target Server Type    : MySQL
 Target Server Version : 50744
 File Encoding         : 65001

 Date: 16/09/2025 02:04:03
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for aircraft_feature_data
-- ----------------------------
DROP TABLE IF EXISTS `aircraft_feature_data`;
CREATE TABLE `aircraft_feature_data`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_type` enum('ECM','ESM','IR','RCS') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '数据类型',
  `aircraft_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '飞机型号',
  `system_type` enum('RADAR','COMM') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '雷达/通信，仅ECM/ESM用',
  `mode_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '工作模式名称，仅ECM/ESM用',
  `power` float NULL DEFAULT NULL COMMENT '发射功率，单位: W',
  `frequency` float NULL DEFAULT NULL COMMENT '中心频率，单位: GHz，ECM/ESM/RCS用',
  `bandwidth` float NULL DEFAULT NULL COMMENT '带宽，单位: MHz',
  `pulse_width` float NULL DEFAULT NULL COMMENT '脉宽，μs，仅ECM/ESM用',
  `pri` float NULL DEFAULT NULL COMMENT '脉冲重复间隔，μs，仅ECM/ESM用',
  `beam_number` int(11) NULL DEFAULT NULL COMMENT '波束号，仅ECM/ESM用',
  `minAz` float NULL DEFAULT NULL COMMENT '最小方位角，仅ECM/ESM用',
  `maxAz` float NULL DEFAULT NULL COMMENT '最大方位角，仅ECM/ESM用',
  `minEle` float NULL DEFAULT NULL COMMENT '最小俯仰角，仅ECM/ESM用',
  `maxEle` float NULL DEFAULT NULL COMMENT '最大俯仰角，仅ECM/ESM用',
  `max_range` float NULL DEFAULT NULL COMMENT '最大识别范围，仅ECM/ESM用',
  `thrust_state` enum('MIL','AB') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '推力状态，仅IR用',
  `env_temperature` int(11) NULL DEFAULT NULL COMMENT '环境温度°C，仅IR用',
  `azimuth` float NULL DEFAULT NULL COMMENT '方位角，仅IR/RCS用',
  `elevation` float NULL DEFAULT NULL COMMENT '俯仰角，仅IR/RCS用',
  `ir_value` double NULL DEFAULT NULL COMMENT '红外特征值，仅IR用',
  `polarization` enum('HH','VV') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '极化方式，仅RCS用',
  `rcs_value` double NULL DEFAULT NULL COMMENT 'RCS值，仅RCS用',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of aircraft_feature_data
-- ----------------------------
INSERT INTO `aircraft_feature_data` VALUES (1, 'ECM', 'F16', 'RADAR', '搜索', 1000, 9.5, 20, 5, 1000, NULL, NULL, NULL, NULL, NULL, 200, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO `aircraft_feature_data` VALUES (2, 'IR', 'F16', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'AB', 20, 30, 0, 120.5, NULL, NULL);
INSERT INTO `aircraft_feature_data` VALUES (3, 'RCS', 'F16', NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 30, 0, NULL, 'HH', -10.5);

SET FOREIGN_KEY_CHECKS = 1;
