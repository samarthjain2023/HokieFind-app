-- MySQL dump 10.13  Distrib 9.6.0, for macos15.7 (arm64)
--
-- Host: localhost    Database: lost_and_found
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
-- GTID / binlog session lines removed for local imports (avoids ERROR 3546 on existing servers)

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `category_name` varchar(100) NOT NULL,
  PRIMARY KEY (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Electronics'),(2,'Clothing'),(3,'Jewelry'),(4,'Bags & Wallets'),(5,'Keys'),(6,'Documents'),(7,'Sports Equipment');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `claim_status`
--

DROP TABLE IF EXISTS `claim_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `claim_status` (
  `status_id` int NOT NULL AUTO_INCREMENT,
  `status_name` varchar(50) NOT NULL,
  PRIMARY KEY (`status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `claim_status`
--

LOCK TABLES `claim_status` WRITE;
/*!40000 ALTER TABLE `claim_status` DISABLE KEYS */;
INSERT INTO `claim_status` VALUES (1,'Pending'),(2,'Under Review'),(3,'Approved'),(4,'Rejected'),(5,'Closed');
/*!40000 ALTER TABLE `claim_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `claims`
--

DROP TABLE IF EXISTS `claims`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `claims` (
  `claim_id` int NOT NULL AUTO_INCREMENT,
  `listing_id` int DEFAULT NULL,
  `claimant_id` int DEFAULT NULL,
  `claim_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `status_id` int DEFAULT NULL,
  `message_to_finder` text,
  PRIMARY KEY (`claim_id`),
  KEY `listing_id` (`listing_id`),
  KEY `claimant_id` (`claimant_id`),
  KEY `status_id` (`status_id`),
  CONSTRAINT `claims_ibfk_1` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`listing_id`),
  CONSTRAINT `claims_ibfk_2` FOREIGN KEY (`claimant_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `claims_ibfk_3` FOREIGN KEY (`status_id`) REFERENCES `claim_status` (`status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `claims`
--

LOCK TABLES `claims` WRITE;
/*!40000 ALTER TABLE `claims` DISABLE KEYS */;
INSERT INTO `claims` VALUES (1,1,4,'2026-03-19 13:28:50',1,'I think this is my iPhone, I lost it after my 2pm class.'),(2,2,5,'2026-03-19 13:28:50',2,'That ring belongs to my girlfriend, she lost it studying.'),(3,3,6,'2026-03-19 13:28:50',3,'Those are my car keys, Honda Civic key with a blue lanyard.'),(4,5,5,'2026-03-19 13:28:50',3,'That is my student ID, Jordan Smith.'),(5,6,4,'2026-03-19 13:28:50',1,'I lost my AirPods at the gym last Tuesday.'),(6,7,6,'2026-03-19 13:28:50',2,'My tennis racket with orange grip tape, lost after practice.'),(7,23,7,'2026-04-23 15:27:23',NULL,'this is my item');
/*!40000 ALTER TABLE `claims` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `item_name` varchar(100) NOT NULL,
  `category_id` int DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `description` text,
  `distinguishing_features` text,
  PRIMARY KEY (`item_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `items_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES (1,'iPhone 15',1,'Black','Apple smartphone','Cracked bottom corner, VT sticker on back'),(2,'AirPods Pro',1,'White','Wireless earbuds with case','Name written inside case lid'),(3,'North Face Jacket',2,'Red','Heavy winter jacket','Torn left pocket zipper'),(4,'Gold Ring',3,'Gold','Plain gold band','Engraving inside: J+M 2022'),(5,'Car Keys',5,'Silver','Honda key with bottle opener','Blue lanyard attached'),(6,'Student ID',6,'White','Virginia Tech student ID card','Name: Jordan Smith'),(7,'Tennis Racket',7,'Blue','Wilson tennis racket','Grip tape replaced with orange');
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `listings`
--

DROP TABLE IF EXISTS `listings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `listings` (
  `listing_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `location_found` varchar(255) DEFAULT NULL,
  `date_posted` datetime DEFAULT CURRENT_TIMESTAMP,
  `status_id` int DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`listing_id`),
  KEY `user_id` (`user_id`),
  KEY `item_id` (`item_id`),
  KEY `status_id` (`status_id`),
  CONSTRAINT `listings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `listings_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`item_id`),
  CONSTRAINT `listings_ibfk_3` FOREIGN KEY (`status_id`) REFERENCES `claim_status` (`status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `listings`
--

LOCK TABLES `listings` WRITE;
/*!40000 ALTER TABLE `listings` DISABLE KEYS */;
INSERT INTO `listings` VALUES (1,2,1,'Torgersen Hall Room 1060','2026-03-19 13:28:50',1,'https://images.example.com/iphone.jpg',NULL,NULL),(2,2,4,'Newman Library 2nd Floor','2026-03-19 13:28:50',1,'https://images.example.com/ring.jpg',NULL,NULL),(3,3,5,'Parking Lot C, Squires','2026-03-19 13:28:50',2,'https://images.example.com/keys.jpg',NULL,NULL),(4,3,3,'Dietrick Dining Hall','2026-03-19 13:28:50',1,'https://images.example.com/jacket.jpg',NULL,NULL),(5,2,6,'McBryde Hall Lobby','2026-03-19 13:28:50',3,'https://images.example.com/id.jpg',NULL,NULL),(6,3,2,'War Memorial Gym','2026-03-19 13:28:50',1,'https://images.example.com/airpods.jpg',NULL,NULL),(7,3,7,'Rector Field House','2026-03-19 13:28:50',2,'https://images.example.com/racket.jpg',NULL,NULL),(9,NULL,NULL,'Alight Blacksburg ','2026-04-01 17:03:37',NULL,'https://alight-blacksburg.com/wp-content/uploads/sites/19/2021/10/ABLA_LogoSpot-VerHIGH-copy.jpg',NULL,NULL),(10,NULL,NULL,'Mccomas Hall','2026-04-03 12:36:22',NULL,'',NULL,NULL),(11,NULL,NULL,'Ambler Johnson Hall','2026-04-03 12:36:59',NULL,'',NULL,NULL),(12,NULL,NULL,'Engel Hall','2026-04-03 12:37:09',NULL,'',NULL,NULL),(13,NULL,NULL,'Latham Hall','2026-04-03 12:37:17',NULL,'',NULL,NULL),(14,NULL,NULL,'Pearson Hall West','2026-04-03 12:37:31',NULL,'',NULL,NULL),(15,NULL,NULL,'Pearson Hall East','2026-04-03 12:37:35',NULL,'',NULL,NULL),(16,NULL,NULL,'Pamplin Hall','2026-04-03 12:37:49',NULL,'',NULL,NULL),(17,NULL,NULL,'Steger Hall','2026-04-03 12:37:56',NULL,'',NULL,NULL),(18,NULL,NULL,'Sheep Barn','2026-04-03 12:38:06',NULL,'',NULL,NULL),(19,NULL,NULL,'Cochrane Hall','2026-04-03 12:38:26',NULL,'',NULL,NULL),(20,NULL,NULL,'Payne Hall','2026-04-03 12:38:36',NULL,'',NULL,NULL),(22,NULL,NULL,'Terraceview Apartments','2026-04-03 13:03:58',NULL,'URL',NULL,NULL),(23,7,NULL,'Newman Hall','2026-04-23 15:19:28',NULL,'','Water Bottle','Black Owala Water Bottle with JJK sticker');
/*!40000 ALTER TABLE `listings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `notification_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `claim_id` int DEFAULT NULL,
  `message` text,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  `read_status` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`notification_id`),
  KEY `user_id` (`user_id`),
  KEY `claim_id` (`claim_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`claim_id`) REFERENCES `claims` (`claim_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,2,1,'Someone has claimed your listing for iPhone 15.','2026-03-19 13:28:50',0),(2,4,1,'Your claim for iPhone 15 has been received.','2026-03-19 13:28:50',1),(3,3,3,'Your listing for Car Keys has been claimed.','2026-03-19 13:28:50',0),(4,5,2,'Your claim for Gold Ring is under review.','2026-03-19 13:28:50',0),(5,2,5,'Someone has claimed your listing for AirPods Pro.','2026-03-19 13:28:50',1),(6,6,3,'Your claim for Car Keys has been approved.','2026-03-19 13:28:50',1);
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) NOT NULL,
  PRIMARY KEY (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Admin'),(2,'Finder'),(3,'Claimant');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transaction_history`
--

DROP TABLE IF EXISTS `transaction_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transaction_history` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `claim_id` int DEFAULT NULL,
  `action_type` varchar(100) DEFAULT NULL,
  `action_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `notes` text,
  PRIMARY KEY (`transaction_id`),
  KEY `claim_id` (`claim_id`),
  CONSTRAINT `transaction_history_ibfk_1` FOREIGN KEY (`claim_id`) REFERENCES `claims` (`claim_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transaction_history`
--

LOCK TABLES `transaction_history` WRITE;
/*!40000 ALTER TABLE `transaction_history` DISABLE KEYS */;
INSERT INTO `transaction_history` VALUES (1,1,'CLAIM_SUBMITTED','2026-03-19 13:28:51','Claimant submitted initial claim for iPhone 15.'),(2,2,'CLAIM_SUBMITTED','2026-03-19 13:28:51','Claim submitted for gold ring found in library.'),(3,3,'CLAIM_APPROVED','2026-03-19 13:28:51','Finder verified car registration, claim approved.'),(4,3,'ITEM_RETURNED','2026-03-19 13:28:51','Keys returned to claimant at Squires front desk.'),(5,4,'CLAIM_APPROVED','2026-03-19 13:28:51','Student ID returned to Jordan Smith.'),(6,5,'CLAIM_SUBMITTED','2026-03-19 13:28:51','AirPods claim submitted, awaiting proof review.'),(7,6,'UNDER_REVIEW','2026-03-19 13:28:51','Tennis racket claim under review by admin.');
/*!40000 ALTER TABLE `transaction_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role_id` int DEFAULT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `role` varchar(20) DEFAULT 'user',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES (1,'Anav','Madan','anav@vt.edu','hash1abc',1,'2026-03-19 13:28:50','user'),(2,'Sarah','Johnson','sarah@vt.edu','hash2abc',2,'2026-03-19 13:28:50','user'),(3,'Marcus','Lee','marcus@vt.edu','hash3abc',2,'2026-03-19 13:28:50','user'),(4,'Priya','Patel','priya@vt.edu','hash4abc',3,'2026-03-19 13:28:50','user'),(5,'Jordan','Smith','jordan@vt.edu','hash5abc',3,'2026-03-19 13:28:50','user'),(6,'Emily','Chen','emily@vt.edu','hash6abc',3,'2026-03-19 13:28:50','user'),(7,'Nitin','Ankareddy','nitinankareddy@vt.edu','$2b$12$KMRPQOzsCjW.0mQh6FFo0uQOKcJ4MU3EogW66NDiD0CmgCVecxZ6C',NULL,'2026-04-23 14:53:49','admin');
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `verification`
--

DROP TABLE IF EXISTS `verification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `verification` (
  `verification_id` int NOT NULL AUTO_INCREMENT,
  `claim_id` int DEFAULT NULL,
  `proof_description` text,
  `proof_image_url` varchar(255) DEFAULT NULL,
  `verified_flag` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`verification_id`),
  KEY `claim_id` (`claim_id`),
  CONSTRAINT `verification_ibfk_1` FOREIGN KEY (`claim_id`) REFERENCES `claims` (`claim_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `verification`
--

LOCK TABLES `verification` WRITE;
/*!40000 ALTER TABLE `verification` DISABLE KEYS */;
INSERT INTO `verification` VALUES (1,1,'Screenshot of phone serial number matching.','https://proof.example.com/v1.jpg',0),(2,2,'Photo of engraving J+M 2022 on another ring.','https://proof.example.com/v2.jpg',0),(3,3,'Photo of car registration matching the keys.','https://proof.example.com/v3.jpg',1),(4,4,'Student ID photo matches claimant face.','https://proof.example.com/v4.jpg',1),(5,5,'Receipt from Apple Store for AirPods Pro.','https://proof.example.com/v5.jpg',0),(6,6,'Photo of racket before it was lost.','https://proof.example.com/v6.jpg',0);
/*!40000 ALTER TABLE `verification` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-24 13:25:49
