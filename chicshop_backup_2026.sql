-- MySQL dump 10.13  Distrib 9.6.0, for Win64 (x86_64)
--
-- Host: localhost    Database: ecom_db
-- ------------------------------------------------------
-- Server version	9.6.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '9c37d0fe-38cd-11f1-a9b0-e4e74997cc78:1-856';

--
-- Table structure for table `accounts_passwordresettoken`
--

DROP TABLE IF EXISTS `accounts_passwordresettoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_passwordresettoken` (
  `id` char(32) NOT NULL,
  `token` varchar(64) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `expires_at` datetime(6) NOT NULL,
  `used` tinyint(1) NOT NULL,
  `user_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `accounts_passwordresettoken_user_id_2789bc5c_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `accounts_passwordresettoken_user_id_2789bc5c_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_passwordresettoken`
--

LOCK TABLES `accounts_passwordresettoken` WRITE;
/*!40000 ALTER TABLE `accounts_passwordresettoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_passwordresettoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user`
--

DROP TABLE IF EXISTS `accounts_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user` (
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `id` char(32) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `address` longtext NOT NULL,
  `city` varchar(100) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_email_verified` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `last_login_ip` char(39) DEFAULT NULL,
  `failed_login_attempts` smallint unsigned NOT NULL,
  `account_locked_until` datetime(6) DEFAULT NULL,
  `marketing_consent` tinyint(1) NOT NULL,
  `terms_accepted_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `accounts_user_chk_1` CHECK ((`failed_login_attempts` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user`
--

LOCK TABLES `accounts_user` WRITE;
/*!40000 ALTER TABLE `accounts_user` DISABLE KEYS */;
INSERT INTO `accounts_user` VALUES ('argon2$argon2id$v=19$m=102400,t=2,p=8$dlVTZHhvcW9lMzVpNTA2YWRPY3V6Mg$MUGqVQJzpzuSJ3d2pFXhrolCklW/VEyHC38qz/Ly0J4','2026-05-31 01:19:19.450010',1,'ed44b58f5c8741f8b348f2c049219110','bhaalpha4@gmail.com','','Alpha Oumar','Bah','','',1,1,0,'2026-05-30 22:51:04.727242',NULL,0,NULL,0,NULL);
/*!40000 ALTER TABLE `accounts_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_groups`
--

DROP TABLE IF EXISTS `accounts_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` char(32) NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_groups_user_id_group_id_59c0b32f_uniq` (`user_id`,`group_id`),
  KEY `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` (`group_id`),
  CONSTRAINT `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `accounts_user_groups_user_id_52b62117_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_groups`
--

LOCK TABLES `accounts_user_groups` WRITE;
/*!40000 ALTER TABLE `accounts_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_user_permissions`
--

DROP TABLE IF EXISTS `accounts_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` char(32) NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq` (`user_id`,`permission_id`),
  KEY `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` (`permission_id`),
  CONSTRAINT `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `accounts_user_user_p_user_id_e4f0a161_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_user_permissions`
--

LOCK TABLES `accounts_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `accounts_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_useraddress`
--

DROP TABLE IF EXISTS `accounts_useraddress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_useraddress` (
  `id` char(32) NOT NULL,
  `label` varchar(50) NOT NULL,
  `address` longtext NOT NULL,
  `city` varchar(100) NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `accounts_useraddress_user_id_5348f16c_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `accounts_useraddress_user_id_5348f16c_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_useraddress`
--

LOCK TABLES `accounts_useraddress` WRITE;
/*!40000 ALTER TABLE `accounts_useraddress` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_useraddress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',3,'add_permission'),(6,'Can change permission',3,'change_permission'),(7,'Can delete permission',3,'delete_permission'),(8,'Can view permission',3,'view_permission'),(9,'Can add group',2,'add_group'),(10,'Can change group',2,'change_group'),(11,'Can delete group',2,'delete_group'),(12,'Can view group',2,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add Blacklisted Token',6,'add_blacklistedtoken'),(22,'Can change Blacklisted Token',6,'change_blacklistedtoken'),(23,'Can delete Blacklisted Token',6,'delete_blacklistedtoken'),(24,'Can view Blacklisted Token',6,'view_blacklistedtoken'),(25,'Can add Outstanding Token',7,'add_outstandingtoken'),(26,'Can change Outstanding Token',7,'change_outstandingtoken'),(27,'Can delete Outstanding Token',7,'delete_outstandingtoken'),(28,'Can view Outstanding Token',7,'view_outstandingtoken'),(29,'Can add utilisateur',9,'add_user'),(30,'Can change utilisateur',9,'change_user'),(31,'Can delete utilisateur',9,'delete_user'),(32,'Can view utilisateur',9,'view_user'),(33,'Can add token de réinitialisation',8,'add_passwordresettoken'),(34,'Can change token de réinitialisation',8,'change_passwordresettoken'),(35,'Can delete token de réinitialisation',8,'delete_passwordresettoken'),(36,'Can view token de réinitialisation',8,'view_passwordresettoken'),(37,'Can add user address',10,'add_useraddress'),(38,'Can change user address',10,'change_useraddress'),(39,'Can delete user address',10,'delete_useraddress'),(40,'Can view user address',10,'view_useraddress'),(41,'Can add catégorie',11,'add_category'),(42,'Can change catégorie',11,'change_category'),(43,'Can delete catégorie',11,'delete_category'),(44,'Can view catégorie',11,'view_category'),(45,'Can add code promo',14,'add_promocode'),(46,'Can change code promo',14,'change_promocode'),(47,'Can delete code promo',14,'delete_promocode'),(48,'Can view code promo',14,'view_promocode'),(49,'Can add produit',12,'add_product'),(50,'Can change produit',12,'change_product'),(51,'Can delete produit',12,'delete_product'),(52,'Can view produit',12,'view_product'),(53,'Can add avis client',13,'add_productreview'),(54,'Can change avis client',13,'change_productreview'),(55,'Can delete avis client',13,'delete_productreview'),(56,'Can view avis client',13,'view_productreview'),(57,'Can add commande',15,'add_order'),(58,'Can change commande',15,'change_order'),(59,'Can delete commande',15,'delete_order'),(60,'Can view commande',15,'view_order'),(61,'Can add ligne de commande',16,'add_orderitem'),(62,'Can change ligne de commande',16,'change_orderitem'),(63,'Can delete ligne de commande',16,'delete_orderitem'),(64,'Can view ligne de commande',16,'view_orderitem'),(65,'Can add paiement',17,'add_payment'),(66,'Can change paiement',17,'change_payment'),(67,'Can delete paiement',17,'delete_payment'),(68,'Can view paiement',17,'view_payment');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2026-05-30 23:02:17.961761','8af296ec-0cab-4b48-8d68-0b26fb3d48ca','Le Duo Essentiel',1,'[{\"added\": {}}]',11,'ed44b58f5c8741f8b348f2c049219110'),(2,'2026-05-30 23:03:05.041129','19deff80-0b92-4a28-a41b-666278d42377','l\'écrin de sérénité',1,'[{\"added\": {}}]',11,'ed44b58f5c8741f8b348f2c049219110'),(3,'2026-05-30 23:03:37.370396','ea9dfa89-8d9e-4eb1-8f94-e5a97384fe96','l\'héritage royal',1,'[{\"added\": {}}]',11,'ed44b58f5c8741f8b348f2c049219110'),(4,'2026-05-30 23:04:39.906679','1fbc9af7-a330-497a-bd1f-8d48eac56b78','BIENVENUE10 — -14%',1,'[{\"added\": {}}]',14,'ed44b58f5c8741f8b348f2c049219110'),(5,'2026-05-30 23:14:44.093715','d25b7861-e77b-43ba-ab5a-9f5de9a195a8','Tapis personnalisé Noire',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(6,'2026-05-30 23:16:19.968553','b3f9df85-4580-4a1d-882e-fb03e4246ddc','Tapis personnalisé Blue',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(7,'2026-05-30 23:18:04.608482','de4a99c7-61bc-4bcd-95d9-c132baadc02f','Tapis personnalisé Gris',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(8,'2026-05-30 23:19:29.969547','3a55bb30-9d8a-469c-87e7-67d3dbb5f757','Tapis personnalisé Belge-Doré',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(9,'2026-05-30 23:23:12.861743','eb205dfe-d8ae-4e86-a0d4-69e900c1d15d','Tapis personnalisé Blue',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(10,'2026-05-30 23:24:49.813368','206d3dd4-7e57-453b-a33e-47b7da900ac7','Tapis personnalisé Gris',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(11,'2026-05-30 23:26:18.703237','7e15acf2-e098-498d-ab6c-13f831799b84','Tapis personnalisé Noire',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(12,'2026-05-30 23:31:17.396631','216058ef-3259-4333-98e3-299a7476835f','Tapis personnalisé Belge',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(13,'2026-05-30 23:33:09.660728','12f551ed-d26b-4f15-b97f-6c4b53dea98d','Tapis personnalisé rose',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(14,'2026-05-30 23:35:12.717965','1954f6fc-c9cb-4dd2-b15a-240fbf951f6a','Tapis personnalisé Rouge',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(15,'2026-05-30 23:37:44.209761','e9e46812-2536-4793-af3c-713d0c06a7f1','Tapis personnalisé Blanc',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(16,'2026-05-31 01:22:42.441625','eb205dfe-d8ae-4e86-a0d4-69e900c1d15d','Tapis personnalisé Blue',2,'[{\"changed\": {\"fields\": [\"Image\"]}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(17,'2026-05-31 01:24:59.092188','fca50e71-f057-4aeb-98ce-1d9c1132508d','Tapis personnalisé Blue',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(18,'2026-05-31 01:27:41.000741','14aab9a4-9eed-487e-bd1d-a108ee71a723','Tapis personnalisé Vert',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(19,'2026-05-31 01:30:11.964544','ae940954-55fe-48bb-be50-546cbf7c27ae','Tapis personnalisé Gris',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(20,'2026-05-31 01:33:24.278577','183c8ac7-0581-4996-ae89-bdb8bf8bfb70','Tapis personnalisé Violet',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(21,'2026-05-31 01:35:19.735268','229a835b-7264-4a98-a8d6-44457e62cba0','Tapis personnalisé Violet',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(22,'2026-05-31 01:41:57.680728','ce0dd607-e392-4f97-9280-ea103d1f350c','Tapis personnalisé Rouge',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(23,'2026-05-31 01:44:51.106538','e9e46812-2536-4793-af3c-713d0c06a7f1','Tapis personnalisé Belge',2,'[{\"changed\": {\"fields\": [\"Name\", \"Slug\"]}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(24,'2026-05-31 01:45:54.197977','216058ef-3259-4333-98e3-299a7476835f','Tapis personnalisé Blanc',2,'[{\"changed\": {\"fields\": [\"Name\", \"Slug\", \"Max embroidery chars\"]}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(25,'2026-05-31 01:51:48.706426','68f24dd5-23b6-429c-9b4e-221f39ad15f9','Tapis personnalisé Blanc',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(26,'2026-05-31 01:53:56.297714','d2afd0ea-4969-49c0-95b2-e09bb7a35a58','Tapis personnalisé Rose',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(27,'2026-05-31 01:57:23.006276','e6cf51c6-7f5a-4cdc-a360-aa361a835126','Tapis personnalisé Noire',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(28,'2026-05-31 02:03:32.897340','677326f4-0bcd-4fb0-b3cf-d9bb91d8b995','Tapis personnalisé Blanc',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110'),(29,'2026-05-31 02:05:59.347766','d3a7be83-d4d8-423d-a33e-d19758949944','Tapis personnalisé Bleu Spécial',1,'[{\"added\": {}}]',12,'ed44b58f5c8741f8b348f2c049219110');
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (8,'accounts','passwordresettoken'),(9,'accounts','user'),(10,'accounts','useraddress'),(1,'admin','logentry'),(2,'auth','group'),(3,'auth','permission'),(4,'contenttypes','contenttype'),(15,'orders','order'),(16,'orders','orderitem'),(17,'payments','payment'),(11,'products','category'),(12,'products','product'),(13,'products','productreview'),(14,'products','promocode'),(5,'sessions','session'),(6,'token_blacklist','blacklistedtoken'),(7,'token_blacklist','outstandingtoken');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-05-30 22:48:21.480361'),(2,'contenttypes','0002_remove_content_type_name','2026-05-30 22:48:22.104006'),(3,'auth','0001_initial','2026-05-30 22:48:23.151768'),(4,'auth','0002_alter_permission_name_max_length','2026-05-30 22:48:23.360407'),(5,'auth','0003_alter_user_email_max_length','2026-05-30 22:48:23.381076'),(6,'auth','0004_alter_user_username_opts','2026-05-30 22:48:23.399934'),(7,'auth','0005_alter_user_last_login_null','2026-05-30 22:48:23.419271'),(8,'auth','0006_require_contenttypes_0002','2026-05-30 22:48:23.425369'),(9,'auth','0007_alter_validators_add_error_messages','2026-05-30 22:48:23.444884'),(10,'auth','0008_alter_user_username_max_length','2026-05-30 22:48:23.464503'),(11,'auth','0009_alter_user_last_name_max_length','2026-05-30 22:48:23.484433'),(12,'auth','0010_alter_group_name_max_length','2026-05-30 22:48:23.529740'),(13,'auth','0011_update_proxy_permissions','2026-05-30 22:48:23.554131'),(14,'auth','0012_alter_user_first_name_max_length','2026-05-30 22:48:23.573081'),(15,'accounts','0001_initial','2026-05-30 22:48:25.690440'),(16,'admin','0001_initial','2026-05-30 22:48:26.221432'),(17,'admin','0002_logentry_remove_auto_add','2026-05-30 22:48:26.255127'),(18,'admin','0003_logentry_add_action_flag_choices','2026-05-30 22:48:26.290660'),(19,'products','0001_initial','2026-05-30 22:48:28.974730'),(20,'products','0002_remove_product_available_sizes_and_more','2026-05-30 22:48:29.362615'),(21,'products','0003_remove_product_available_person_and_more','2026-05-30 22:48:30.076946'),(22,'products','0004_remove_product_short_description','2026-05-30 22:48:30.482741'),(23,'products','0005_product_short_description','2026-05-30 22:48:30.915855'),(24,'products','0006_alter_product_included_items','2026-05-30 22:48:31.682853'),(25,'products','0007_personal_message','2026-05-30 22:48:33.397928'),(26,'products','0008_remove_product_available_sizes_and_more','2026-05-30 22:48:34.198507'),(27,'products','0009_product_embroidery_required','2026-05-30 22:48:34.573886'),(28,'orders','0001_initial','2026-05-30 22:48:36.010587'),(29,'sessions','0001_initial','2026-05-30 22:48:36.204027'),(30,'token_blacklist','0001_initial','2026-05-30 22:48:36.828640'),(31,'token_blacklist','0002_outstandingtoken_jti_hex','2026-05-30 22:48:37.239157'),(32,'token_blacklist','0003_auto_20171017_2007','2026-05-30 22:48:37.492351'),(33,'token_blacklist','0004_auto_20171017_2013','2026-05-30 22:48:38.107164'),(34,'token_blacklist','0005_remove_outstandingtoken_jti','2026-05-30 22:48:38.446386'),(35,'token_blacklist','0006_auto_20171017_2113','2026-05-30 22:48:38.543475'),(36,'token_blacklist','0007_auto_20171017_2214','2026-05-30 22:48:39.446562'),(37,'token_blacklist','0008_migrate_to_bigautofield','2026-05-30 22:48:40.363649'),(38,'token_blacklist','0010_fix_migrate_to_bigautofield','2026-05-30 22:48:40.467839'),(39,'token_blacklist','0011_linearizes_history','2026-05-30 22:48:40.491760'),(40,'token_blacklist','0012_alter_outstandingtoken_user','2026-05-30 22:48:40.628059'),(41,'token_blacklist','0013_alter_blacklistedtoken_options_and_more','2026-05-30 22:48:40.717175');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders_order`
--

DROP TABLE IF EXISTS `orders_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders_order` (
  `id` char(32) NOT NULL,
  `reference` varchar(20) NOT NULL,
  `customer_first_name` varchar(50) NOT NULL,
  `customer_last_name` varchar(50) NOT NULL,
  `customer_email` varchar(254) NOT NULL,
  `customer_phone` varchar(20) NOT NULL,
  `delivery_address` longtext NOT NULL,
  `delivery_city` varchar(100) NOT NULL,
  `delivery_instructions` longtext NOT NULL,
  `embroidery_name` varchar(20) NOT NULL,
  `personal_message` varchar(200) NOT NULL,
  `subtotal` decimal(12,0) NOT NULL,
  `discount_amount` decimal(12,0) NOT NULL,
  `total_amount` decimal(12,0) NOT NULL,
  `promo_code` varchar(30) NOT NULL,
  `payment_method` varchar(20) NOT NULL,
  `payment_status` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `admin_notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `confirmed_at` datetime(6) DEFAULT NULL,
  `delivered_at` datetime(6) DEFAULT NULL,
  `user_id` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference` (`reference`),
  KEY `orders_orde_status_079368_idx` (`status`,`created_at` DESC),
  KEY `orders_orde_custome_ca0107_idx` (`customer_email`),
  KEY `orders_orde_referen_cf3026_idx` (`reference`),
  KEY `orders_order_user_id_e9b59eb1_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `orders_order_user_id_e9b59eb1_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders_order`
--

LOCK TABLES `orders_order` WRITE;
/*!40000 ALTER TABLE `orders_order` DISABLE KEYS */;
INSERT INTO `orders_order` VALUES ('09aae782388f405f9968e7f0432dab9d','CS-879OKHOS','Alpha','Bah','bhaalpha4@gmail.com','0586838902','Boulevard de France','Bingerville','','','',11990,0,11990,'','cash','pending','pending','','2026-05-30 23:27:34.448940','2026-05-30 23:27:34.449028',NULL,NULL,'ed44b58f5c8741f8b348f2c049219110'),('4f49b33ca9fc4aaebd9ace972e43fd6f','CS-ZPKLM53K','Alpha','Bah','bhaalpha4@gmail.com','0586838902','Boulevard de France','Cocody','yuiopolk jhjkop','','',11990,0,11990,'','wave','pending','pending','','2026-05-31 03:06:20.320868','2026-05-31 03:06:20.320966',NULL,NULL,'ed44b58f5c8741f8b348f2c049219110'),('a1a97bbae7604c4f9de341ffffa815e1','CS-5BMNAKYQ','Alpha','Bah','bhaalpha4@gmail.com','0586838902','Boulevard de France','Cocody','','','',11990,0,11990,'','cash','pending','pending','','2026-05-31 02:12:48.461005','2026-05-31 02:12:48.461085',NULL,NULL,'ed44b58f5c8741f8b348f2c049219110'),('a5907827bb144f988e3288cbf9a15c2e','CS-O02X6T22','Alpha','Bah','bhaalpha4@gmail.com','0586838902','Boulevard de France','Marcory','fghj guhio tfyguj uijkn ghjhj,','','',79400,0,79400,'','orange_money','pending','confirmed','','2026-05-31 03:11:16.155058','2026-05-31 03:13:25.883973','2026-05-31 03:13:25.883740',NULL,'ed44b58f5c8741f8b348f2c049219110'),('fadec5aedd0a4b2083dbc822051120b7','CS-HV9A3HVM','Alpha','Bah','bhaalpha4@gmail.com','0586838902','Boulevard de France','Port-Bouët','','','',11990,0,11990,'','cash','pending','pending','','2026-05-31 03:07:55.717989','2026-05-31 03:07:55.718058',NULL,NULL,'ed44b58f5c8741f8b348f2c049219110');
/*!40000 ALTER TABLE `orders_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders_orderitem`
--

DROP TABLE IF EXISTS `orders_orderitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders_orderitem` (
  `id` char(32) NOT NULL,
  `product_name` varchar(200) NOT NULL,
  `unit_price` decimal(10,0) NOT NULL,
  `quantity` smallint unsigned NOT NULL,
  `embroidery_name` varchar(20) NOT NULL,
  `personal_message` varchar(200) NOT NULL,
  `order_id` char(32) NOT NULL,
  `product_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `orders_orderitem_order_id_fe61a34d_fk_orders_order_id` (`order_id`),
  KEY `orders_orderitem_product_id_afe4254a_fk_products_product_id` (`product_id`),
  CONSTRAINT `orders_orderitem_order_id_fe61a34d_fk_orders_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders_order` (`id`),
  CONSTRAINT `orders_orderitem_product_id_afe4254a_fk_products_product_id` FOREIGN KEY (`product_id`) REFERENCES `products_product` (`id`),
  CONSTRAINT `orders_orderitem_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders_orderitem`
--

LOCK TABLES `orders_orderitem` WRITE;
/*!40000 ALTER TABLE `orders_orderitem` DISABLE KEYS */;
INSERT INTO `orders_orderitem` VALUES ('126b623a768c4626a18268dfe54a1c72','Tapis personnalisé Gris',11990,1,'Bah Alpha Oumar','Q\'allah mes la baracat sur votre famille','09aae782388f405f9968e7f0432dab9d','de4a99c761bc4bcd95d9c132baadc02f'),('28a30c03be294572821110c7c834e727','Tapis personnalisé Noire',19850,1,'Bah Alpha Oumar','Q\'allah mes la baracat sur votre famille','a5907827bb144f988e3288cbf9a15c2e','d25b7861e77b43baab5a9f5de9a195a8'),('6c888ac97f334defaf3a6c8bfe62e9b4','Tapis personnalisé Blanc',19850,1,'Bah Alpha Oumar','Q\'allah mes la baracat sur votre famille','a5907827bb144f988e3288cbf9a15c2e','677326f40bcd4fb0b3cfd9bb91d8b995'),('94fefa170a6e47d98137b59554194581','Tapis personnalisé Vert',11990,1,'Bah Alpha Oumar','','4f49b33ca9fc4aaebd9ace972e43fd6f','14aab9a49eed487ebd1da108ee71a723'),('9f6a2362798e433dbd0de6b55cecbc83','Tapis personnalisé Bleu Spécial',19850,1,'Bah Alpha Oumar','Q\'allah mes la baracat sur votre famille','a5907827bb144f988e3288cbf9a15c2e','d3a7be83d4d8423da33ed19758949944'),('b1956c5498a8435a8d114c6dbb5fc9e0','Tapis personnalisé Violet',11990,1,'Bah Alpha Oumar','Q\'allah mes la baracat sur votre famille','fadec5aedd0a4b2083dbc822051120b7','229a835b72644a98a8d644457e62cba0'),('bba3ad81961d4042a75e60940ace484b','Tapis personnalisé Violet',19850,1,'Bah Alpha Oumar','Q\'allah mes la baracat sur votre famille','a5907827bb144f988e3288cbf9a15c2e','183c8ac705814996ae89bdb8bf8bfb70'),('c591b1d6b5614b78a66e2e450f6d4c4d','Tapis personnalisé Gris',11990,1,'Bah Alpha Oumar','Q\'allah mes la baracat sur votre famille','a1a97bbae7604c4f9de341ffffa815e1','de4a99c761bc4bcd95d9c132baadc02f');
/*!40000 ALTER TABLE `orders_orderitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products_category`
--

DROP TABLE IF EXISTS `products_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products_category` (
  `id` char(32) NOT NULL,
  `name` varchar(100) NOT NULL,
  `slug` varchar(120) NOT NULL,
  `description` longtext NOT NULL,
  `icon` varchar(10) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `order` smallint unsigned NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  CONSTRAINT `products_category_chk_1` CHECK ((`order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products_category`
--

LOCK TABLES `products_category` WRITE;
/*!40000 ALTER TABLE `products_category` DISABLE KEYS */;
INSERT INTO `products_category` VALUES ('19deff800b924a28a41b666278d42377','l\'écrin de sérénité','lecrin-de-serenite','','✨',1,15,'2026-05-30 23:03:05.039049'),('8af296ec0cab4b488d680b26fb3d48ca','Le Duo Essentiel','le-duo-essentiel','','🕌',1,15,'2026-05-30 23:02:17.959489'),('ea9dfa898d9e4eb18f94e5a97384fe96','l\'héritage royal','lheritage-royal','','👑',1,15,'2026-05-30 23:03:37.368580');
/*!40000 ALTER TABLE `products_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products_product`
--

DROP TABLE IF EXISTS `products_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products_product` (
  `id` char(32) NOT NULL,
  `name` varchar(200) NOT NULL,
  `slug` varchar(220) NOT NULL,
  `description` longtext NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `original_price` decimal(10,0) DEFAULT NULL,
  `stock_quantity` int unsigned NOT NULL,
  `is_available` tinyint(1) NOT NULL,
  `allows_embroidery` tinyint(1) NOT NULL,
  `max_embroidery_chars` smallint unsigned NOT NULL,
  `badge` varchar(10) NOT NULL,
  `emoji` varchar(10) NOT NULL,
  `color` varchar(100) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `included_items` longtext,
  `views_count` int unsigned NOT NULL,
  `sales_count` int unsigned NOT NULL,
  `is_featured` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `category_id` char(32) NOT NULL,
  `short_description` longtext,
  `allows_personal_message` tinyint(1) NOT NULL,
  `max_message_chars` smallint unsigned NOT NULL,
  `embroidery_required` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `products_pr_is_acti_867533_idx` (`is_active`,`is_available`),
  KEY `products_pr_categor_50f5f1_idx` (`category_id`,`is_active`),
  KEY `products_pr_sales_c_6796bf_idx` (`sales_count` DESC),
  CONSTRAINT `products_product_category_id_9b594869_fk_products_category_id` FOREIGN KEY (`category_id`) REFERENCES `products_category` (`id`),
  CONSTRAINT `products_product_chk_1` CHECK ((`stock_quantity` >= 0)),
  CONSTRAINT `products_product_chk_2` CHECK ((`max_embroidery_chars` >= 0)),
  CONSTRAINT `products_product_chk_3` CHECK ((`views_count` >= 0)),
  CONSTRAINT `products_product_chk_4` CHECK ((`sales_count` >= 0)),
  CONSTRAINT `products_product_chk_5` CHECK ((`max_message_chars` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products_product`
--

LOCK TABLES `products_product` WRITE;
/*!40000 ALTER TABLE `products_product` DISABLE KEYS */;
INSERT INTO `products_product` VALUES ('12f551edd26b4f15b97f6c4b53dea98d','Tapis personnalisé rose','tapis-personnalise-rose-duo','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',8990,10900,0,1,1,20,'HOT','🌹🎉','Rose','products/tapis_rose_4_ayyO4JA.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nChapelet,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-30 23:33:09.657091','2026-05-30 23:33:09.657174','8af296ec0cab4b488d680b26fb3d48ca','',0,200,1),('14aab9a49eed487ebd1da108ee71a723','Tapis personnalisé Vert','tapis-personnalise-vert','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',11990,14000,3,1,1,20,'NEW','❤✨','Vert','products/tapis_vert_OLSGx1J.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nEmballage cadeau soigné\"',1,1,1,1,'2026-05-31 01:27:40.997351','2026-05-31 01:27:40.997473','8af296ec0cab4b488d680b26fb3d48ca','',0,200,1),('183c8ac705814996ae89bdb8bf8bfb70','Tapis personnalisé Violet','tapis-personnalise-violet-hr','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',19850,24000,4,1,1,45,'NEW','💖😍','Violet','products/tapis_violet_2_U0jffGe.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nEmballage cadeau soigné\"',1,1,1,1,'2026-05-31 01:33:24.274494','2026-05-31 01:33:24.274571','ea9dfa898d9e4eb18f94e5a97384fe96','',1,200,1),('1954f6fcc9cb4dd2b15a240fbf951f6a','Tapis personnalisé Rouge','tapis-personnalise-rouge-duo','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',8990,10900,3,1,1,20,'NEW','❤','Rouge','products/tapis_rouge_2_XEPJNkh.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nChapelet,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-30 23:35:12.715070','2026-05-30 23:35:12.715152','8af296ec0cab4b488d680b26fb3d48ca','',0,200,1),('206d3dd47e57453ba33e47b7da900ac7','Tapis personnalisé Gris','tapis-personnalise-gris-duo','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',8990,10896,4,1,1,20,'HOT','💖😍','Gris','products/tapis_gris_4.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nChapelet,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-30 23:24:49.810472','2026-05-30 23:24:49.810555','8af296ec0cab4b488d680b26fb3d48ca','',0,200,1),('216058ef3259433398e3299a7476835f','Tapis personnalisé Blanc','tapis-personnalise-blanc-duo','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',8990,10900,0,1,1,50,'HOT','💖😍','Belge','products/WhatsApp_Image_2026-04-09_at_03.27.07.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nChapelet,\r\nEmballage cadeau soigné\"',1,0,1,1,'2026-05-30 23:31:17.393514','2026-05-31 01:45:54.193547','8af296ec0cab4b488d680b26fb3d48ca','',0,200,1),('229a835b72644a98a8d644457e62cba0','Tapis personnalisé Violet','tapis-personnalise-violet-ecr','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',11990,14000,5,1,1,50,'HOT','🌹🎉','Violet','products/tapis_violet.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nEmballage cadeau soigné\"',2,1,1,1,'2026-05-31 01:35:19.732117','2026-05-31 01:35:19.732195','19deff800b924a28a41b666278d42377','',1,200,1),('3a55bb309d8a469c87e767d3dbb5f757','Tapis personnalisé Belge-Doré','tapis-personnalise-belge-dore','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',11990,14000,2,1,1,20,'NEW','❤','Belge','products/tapis_belge_dore_ILvANmm.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nBoubou marocain (H ou F),\r\nParfum de luxe,\r\nEmballage cadeau soigné\"',2,0,1,1,'2026-05-30 23:19:29.965482','2026-05-30 23:19:29.965560','19deff800b924a28a41b666278d42377','',1,200,1),('677326f40bcd4fb0b3cfd9bb91d8b995','Tapis personnalisé Blanc','tapis-personnalise-blanc-hr','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',19850,24000,4,1,1,50,'HOT','💖😍','Blanc','products/tapis_blanc.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nBoubou marocain (H ou F),\r\nParfum de luxe,\r\nEmballage cadeau soigné\"',3,1,1,1,'2026-05-31 02:03:32.893796','2026-05-31 02:03:32.893887','ea9dfa898d9e4eb18f94e5a97384fe96','',1,200,1),('68f24dd523b6429c9b4e221f39ad15f9','Tapis personnalisé Blanc','tapis-personnalise-blanc-ecr','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',12990,14000,3,1,1,50,'HOT','🌹🎉','Blanc','products/tapisblanc.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-31 01:51:48.701480','2026-05-31 01:51:48.701561','19deff800b924a28a41b666278d42377','',1,200,1),('7e15acf2e098498dab6c13f831799b84','Tapis personnalisé Noire','tapis-personnalise-noire-duo','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',8990,10892,4,1,1,20,'HOT','😎✔✨','Noire','products/tapis_noire_2_VAJzFvu.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nChapelet,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-30 23:26:18.700528','2026-05-30 23:26:18.700601','8af296ec0cab4b488d680b26fb3d48ca','',0,200,1),('ae94095455fe48bbbe50546cbf7c27ae','Tapis personnalisé Gris','tapis-personnalise-gris-ecr','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',11990,13999,3,1,1,30,'NEW','💖😍','Gris','products/tapis_gris_5_bVXvotx.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-31 01:30:11.961067','2026-05-31 01:30:11.961145','19deff800b924a28a41b666278d42377','',1,200,1),('b3f9df8545804a1d882efb03e4246ddc','Tapis personnalisé Blue','tapis-personnalise-blue','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',19850,24000,3,1,1,20,'HOT','😎✔✨','Bleu','products/tapis_bleu_3_5oJUHkT.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nBoubou marocain (H ou F),\r\nParfum de luxe,\r\nEmballage cadeau soigné\"',1,0,1,1,'2026-05-30 23:16:19.965783','2026-05-30 23:16:19.965862','ea9dfa898d9e4eb18f94e5a97384fe96','',1,200,1),('ce0dd607e3924f979280ea103d1f350c','Tapis personnalisé Rouge','tapis-personnalise-rouge-ecr','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',11990,14000,2,1,1,50,'HOT','💖😍','Rouge','products/tapisrouge.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nEmballage cadeau soigné\"',2,0,1,1,'2026-05-31 01:41:57.675637','2026-05-31 01:41:57.675719','19deff800b924a28a41b666278d42377','',1,200,1),('d25b7861e77b43baab5a9f5de9a195a8','Tapis personnalisé Noire','tapis-personnalise-noire','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',19850,24000,5,1,1,20,'HOT','😎✔✨','Noire','products/tapis_noire_3_6eP9ize.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nBoubou marocain (H ou F),\r\nParfum de luxe,\r\nEmballage cadeau soigné\"',1,1,1,1,'2026-05-30 23:14:44.090820','2026-05-30 23:14:44.090909','ea9dfa898d9e4eb18f94e5a97384fe96','',1,200,1),('d2afd0ea496949c095b2e09bb7a35a58','Tapis personnalisé Rose','tapis-personnalise-rose-ecr','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',11990,14000,3,1,1,50,'HOT','🌹🎉','Rose','products/tapis_rose_3.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-31 01:53:56.292376','2026-05-31 01:53:56.292767','19deff800b924a28a41b666278d42377','',1,200,1),('d3a7be83d4d8423da33ed19758949944','Tapis personnalisé Bleu Spécial','tapis-personnalise-bleu-special','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',19850,24000,2,1,1,49,'NEW','💖😍','Bleu','products/tapsi_bleu_roi_R72nBoX.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nBoubou marocain (H ou F),\r\nParfum de luxe,\r\nEmballage cadeau soigné\"',2,1,1,1,'2026-05-31 02:05:59.344007','2026-05-31 02:05:59.344095','ea9dfa898d9e4eb18f94e5a97384fe96','',1,200,1),('de4a99c761bc4bcd95d9c132baadc02f','Tapis personnalisé Gris','tapis-personnalise-gris','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',11990,13990,3,1,1,20,'PROMO','🌹🎉','Gris','products/tapis_gris_2_ZXSI3HS.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nBoubou marocain (H ou F),\r\nParfum de luxe,\r\nEmballage cadeau soigné\"',2,2,1,1,'2026-05-30 23:18:04.605739','2026-05-30 23:18:04.605809','19deff800b924a28a41b666278d42377','',1,200,1),('e6cf51c67f5a4cdca360aa361a835126','Tapis personnalisé Noire','tapis-personnalise-noire-ecr','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',11880,14000,4,1,1,49,'NEW','😎✔✨','Noire','products/tapis_noire_4_la1DaM5.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-31 01:57:23.001592','2026-05-31 01:57:23.001680','19deff800b924a28a41b666278d42377','',1,200,1),('e9e4681225364793af3c713d0c06a7f1','Tapis personnalisé Belge','tapis-personnalise-belge-du','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',9700,10995,2,1,1,20,'HOT','😎✔✨','Blanc','products/tapis_belge_2.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nChapelet,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-30 23:37:44.206880','2026-05-31 01:44:51.102106','8af296ec0cab4b488d680b26fb3d48ca','',0,200,1),('eb205dfed8ae4e86a0d469e900c1d15d','Tapis personnalisé Blue','tapis-personnalise-blue-duo','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',8990,10900,0,1,1,20,'HOT','❤✨','Bleu','products/tapis_bleu_2_RllNTKu.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nChapelet,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-30 23:23:12.858742','2026-05-31 01:22:42.436098','8af296ec0cab4b488d680b26fb3d48ca','',0,200,1),('fca50e71f0574aeb98ce1d9c1132508d','Tapis personnalisé Blue','tapis-personnalise-blue-ecr','Grand Tapis de Luxe. Epais avec dessous doux antidérapant. Très Doux au toucher avec motif sous forme de Mihrab.',11990,14000,4,1,1,20,'NEW','❤','Bleu','products/tapis_bleu.jpeg','\"Tapis Personnalisé (Nom & Prénom),\r\nMessage personnalisé,\r\nSaint Coran arabe/français,\r\nChapelet + Zikromètre,\r\nEmballage cadeau soigné\"',0,0,1,1,'2026-05-31 01:24:59.088513','2026-05-31 01:24:59.088615','19deff800b924a28a41b666278d42377','',1,200,1);
/*!40000 ALTER TABLE `products_product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products_productreview`
--

DROP TABLE IF EXISTS `products_productreview`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products_productreview` (
  `id` char(32) NOT NULL,
  `author_name` varchar(100) NOT NULL,
  `author_city` varchar(100) NOT NULL,
  `rating` smallint unsigned NOT NULL,
  `comment` longtext NOT NULL,
  `is_approved` tinyint(1) NOT NULL,
  `is_verified_purchase` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `product_id` char(32) NOT NULL,
  `user_id` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `products_productreview_product_id_user_id_8cc1724b_uniq` (`product_id`,`user_id`),
  KEY `products_productreview_user_id_5c551aaa_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `products_productrevi_product_id_7e81c4a6_fk_products_` FOREIGN KEY (`product_id`) REFERENCES `products_product` (`id`),
  CONSTRAINT `products_productreview_user_id_5c551aaa_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `products_productreview_chk_1` CHECK ((`rating` >= 0)),
  CONSTRAINT `rating_range` CHECK (((`rating` >= 1) and (`rating` <= 5)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products_productreview`
--

LOCK TABLES `products_productreview` WRITE;
/*!40000 ALTER TABLE `products_productreview` DISABLE KEYS */;
/*!40000 ALTER TABLE `products_productreview` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products_promocode`
--

DROP TABLE IF EXISTS `products_promocode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products_promocode` (
  `id` char(32) NOT NULL,
  `code` varchar(30) NOT NULL,
  `discount_percent` smallint unsigned NOT NULL,
  `max_uses` int unsigned NOT NULL,
  `current_uses` int unsigned NOT NULL,
  `min_order_amount` decimal(10,0) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `valid_from` datetime(6) NOT NULL,
  `valid_until` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  CONSTRAINT `products_promocode_chk_1` CHECK ((`discount_percent` >= 0)),
  CONSTRAINT `products_promocode_chk_2` CHECK ((`max_uses` >= 0)),
  CONSTRAINT `products_promocode_chk_3` CHECK ((`current_uses` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products_promocode`
--

LOCK TABLES `products_promocode` WRITE;
/*!40000 ALTER TABLE `products_promocode` DISABLE KEYS */;
INSERT INTO `products_promocode` VALUES ('1fbc9af7a330497abd1f8d48eac56b78','BIENVENUE10',14,97,0,0,1,'2026-05-15 00:00:00.000000','2026-07-11 00:00:00.000000','2026-05-30 23:04:39.903645');
/*!40000 ALTER TABLE `products_promocode` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_blacklistedtoken`
--

DROP TABLE IF EXISTS `token_blacklist_blacklistedtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_id` (`token_id`),
  CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_blacklistedtoken`
--

LOCK TABLES `token_blacklist_blacklistedtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_outstandingtoken`
--

DROP TABLE IF EXISTS `token_blacklist_outstandingtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` char(32) DEFAULT NULL,
  `jti` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  KEY `token_blacklist_outs_user_id_83bc629a_fk_accounts_` (`user_id`),
  CONSTRAINT `token_blacklist_outs_user_id_83bc629a_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_outstandingtoken`
--

LOCK TABLES `token_blacklist_outstandingtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-03  9:44:50
