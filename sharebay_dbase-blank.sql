-- MySQL dump 10.13  Distrib 8.0.33, for macos13.3 (arm64)
--
-- Host: localhost    Database: sharebay_dbase
-- ------------------------------------------------------
-- Server version	8.0.33

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

--
-- Table structure for table `activity`
--

DROP TABLE IF EXISTS `activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `actor_id` int NOT NULL,
  `object_type` varchar(50) NOT NULL,
  `object_id` int NOT NULL,
  `image` varchar(100) NOT NULL,
  `text` mediumtext NOT NULL,
  `link` varchar(150) NOT NULL,
  `location` varchar(150) NOT NULL,
  `data` varchar(250) NOT NULL,
  `timestamp` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3746 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity`
--

LOCK TABLES `activity` WRITE;
/*!40000 ALTER TABLE `activity` DISABLE KEYS */;
/*!40000 ALTER TABLE `activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `blog`
--

DROP TABLE IF EXISTS `blog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `blog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `slug` varchar(200) NOT NULL,
  `image` varchar(200) NOT NULL,
  `summary` text NOT NULL,
  `content` mediumtext NOT NULL,
  `author_id` int NOT NULL,
  `timestamp` int NOT NULL,
  `rank` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blog`
--

LOCK TABLES `blog` WRITE;
/*!40000 ALTER TABLE `blog` DISABLE KEYS */;
/*!40000 ALTER TABLE `blog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category` varchar(100) NOT NULL,
  `transactable` tinyint NOT NULL COMMENT '1 = transactable',
  `tags` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Accommodation',1,''),(2,'Help & Advice',1,''),(3,'Gardening & Agricultural',1,''),(4,'Appliances',1,''),(5,'Art & Photography',1,''),(6,'Arts & Crafts',1,''),(7,'Baby & Kids',1,''),(8,'Beauty & Cosmetics',1,''),(9,'Bicycles',1,''),(10,'Books',1,''),(11,'Cars & Motorbikes',1,''),(12,'CDs, DVDs & Vinyl',1,''),(13,'Childcare',1,''),(14,'Clothes & Shoes',1,''),(15,'Community Notices',0,''),(16,'Computer & Accessories',1,''),(17,'Driving & Transport',1,''),(18,'Education & Knowledge',1,''),(19,'Electronics',1,''),(20,'Emergency Aid',1,''),(21,'Food & Drink',1,''),(22,'Friends & Dating',0,''),(23,'General Help',1,''),(24,'Graphic & Web Design',1,''),(25,'Health & Wellbeing',1,''),(26,'Home & Garden',1,''),(27,'Building & Industrial',1,''),(28,'Jewellery',1,''),(29,'Kitchen & Household',1,''),(30,'Land & Real Estate',1,''),(31,'Legal & Accounting Advice',1,''),(32,'Marketing & Promotion',1,''),(33,'Meet-Ups & Collaborations',0,''),(34,'Music & Audio',1,''),(35,'Office & Stationery',1,''),(36,'Pets & Pet Minding',1,''),(37,'Phones & Accessories',1,''),(38,'Programming',1,''),(39,'Sports & Fitness',1,''),(40,'Technical Support',1,''),(41,'Events & Tickets',1,''),(42,'Tools',1,''),(43,'Toys & Games',1,''),(44,'TV & Electronics',1,''),(45,'Writing & Editing',1,''),(46,'Video & Animation',1,''),(47,'Other',1,''),(48,'Translation',1,''),(49,'Cooking',1,''),(50,'Eco Tech & Advice',1,''),(51,'Share Points',0,'');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `countries`
--

DROP TABLE IF EXISTS `countries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `countries` (
  `iso` char(2) NOT NULL,
  `country` varchar(80) NOT NULL,
  PRIMARY KEY (`iso`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `countries`
--

LOCK TABLES `countries` WRITE;
/*!40000 ALTER TABLE `countries` DISABLE KEYS */;
INSERT INTO `countries` VALUES ('AF','Afghanistan'),('AL','Albania'),('DZ','Algeria'),('AS','American Samoa'),('AD','Andorra'),('AO','Angola'),('AI','Anguilla'),('AQ','Antarctica'),('AG','Antigua and Barbuda'),('AR','Argentina'),('AM','Armenia'),('AW','Aruba'),('AU','Australia'),('AT','Austria'),('AZ','Azerbaijan'),('BS','Bahamas'),('BH','Bahrain'),('BD','Bangladesh'),('BB','Barbados'),('BY','Belarus'),('BE','Belgium'),('BZ','Belize'),('BJ','Benin'),('BM','Bermuda'),('BT','Bhutan'),('BO','Bolivia'),('BA','Bosnia and Herzegovina'),('BW','Botswana'),('BV','Bouvet Island'),('BR','Brazil'),('IO','British Indian Ocean Territory'),('BN','Brunei Darussalam'),('BG','Bulgaria'),('BF','Burkina Faso'),('BI','Burundi'),('KH','Cambodia'),('CM','Cameroon'),('CA','Canada'),('CV','Cape Verde'),('KY','Cayman Islands'),('CF','Central African Republic'),('TD','Chad'),('CL','Chile'),('CN','China'),('CX','Christmas Island'),('CC','Cocos (Keeling) Islands'),('CO','Colombia'),('KM','Comoros'),('CG','Congo'),('CD','Congo, the Democratic Republic of the'),('CK','Cook Islands'),('CR','Costa Rica'),('CI','Cote D\'Ivoire'),('HR','Croatia'),('CU','Cuba'),('CY','Cyprus'),('CZ','Czech Republic'),('DK','Denmark'),('DJ','Djibouti'),('DM','Dominica'),('DO','Dominican Republic'),('EC','Ecuador'),('EG','Egypt'),('SV','El Salvador'),('GQ','Equatorial Guinea'),('ER','Eritrea'),('EE','Estonia'),('ET','Ethiopia'),('FK','Falkland Islands (Malvinas)'),('FO','Faroe Islands'),('FJ','Fiji'),('FI','Finland'),('FR','France'),('GF','French Guiana'),('PF','French Polynesia'),('TF','French Southern Territories'),('GA','Gabon'),('GM','Gambia'),('GE','Georgia'),('DE','Germany'),('GH','Ghana'),('GI','Gibraltar'),('GR','Greece'),('GL','Greenland'),('GD','Grenada'),('GP','Guadeloupe'),('GU','Guam'),('GT','Guatemala'),('GN','Guinea'),('GW','Guinea-Bissau'),('GY','Guyana'),('HT','Haiti'),('HM','Heard Island and Mcdonald Islands'),('VA','Holy See (Vatican City State)'),('HN','Honduras'),('HK','Hong Kong'),('HU','Hungary'),('IS','Iceland'),('IN','India'),('ID','Indonesia'),('IR','Iran, Islamic Republic of'),('IQ','Iraq'),('IE','Ireland'),('IL','Israel'),('IT','Italy'),('JM','Jamaica'),('JP','Japan'),('JO','Jordan'),('KZ','Kazakhstan'),('KE','Kenya'),('KI','Kiribati'),('KP','Korea, Democratic People\'s Republic of'),('KR','Korea, Republic of'),('KW','Kuwait'),('KG','Kyrgyzstan'),('LA','Lao People\'s Democratic Republic'),('LV','Latvia'),('LB','Lebanon'),('LS','Lesotho'),('LR','Liberia'),('LY','Libyan Arab Jamahiriya'),('LI','Liechtenstein'),('LT','Lithuania'),('LU','Luxembourg'),('MO','Macao'),('MK','Macedonia, Republic of'),('MG','Madagascar'),('MW','Malawi'),('MY','Malaysia'),('MV','Maldives'),('ML','Mali'),('MT','Malta'),('MH','Marshall Islands'),('MQ','Martinique'),('MR','Mauritania'),('MU','Mauritius'),('YT','Mayotte'),('MX','Mexico'),('FM','Micronesia, Federated States of'),('MD','Moldova, Republic of'),('MC','Monaco'),('MN','Mongolia'),('MS','Montserrat'),('MA','Morocco'),('MZ','Mozambique'),('MM','Myanmar'),('NA','Namibia'),('NR','Nauru'),('NP','Nepal'),('NL','Netherlands'),('AX','&#x00C5;land Islands'),('NC','New Caledonia'),('NZ','New Zealand'),('NI','Nicaragua'),('NE','Niger'),('NG','Nigeria'),('NU','Niue'),('NF','Norfolk Island'),('MP','Northern Mariana Islands'),('NO','Norway'),('OM','Oman'),('PK','Pakistan'),('PW','Palau'),('PS','Palestinian Territory, Occupied'),('PA','Panama'),('PG','Papua New Guinea'),('PY','Paraguay'),('PE','Peru'),('PH','Philippines'),('PN','Pitcairn'),('PL','Poland'),('PT','Portugal'),('PR','Puerto Rico'),('QA','Qatar'),('RE','Reunion'),('RO','Romania'),('RU','Russian Federation'),('RW','Rwanda'),('SH','Saint Helena'),('KN','Saint Kitts and Nevis'),('LC','Saint Lucia'),('PM','Saint Pierre and Miquelon'),('VC','Saint Vincent and the Grenadines'),('WS','Samoa'),('SM','San Marino'),('ST','Sao Tome and Principe'),('SA','Saudi Arabia'),('SN','Senegal'),('RS','Serbia'),('SC','Seychelles'),('SL','Sierra Leone'),('SG','Singapore'),('SK','Slovakia'),('SI','Slovenia'),('SB','Solomon Islands'),('SO','Somalia'),('ZA','South Africa'),('GS','South Georgia and the South Sandwich Islands'),('ES','Spain'),('LK','Sri Lanka'),('SD','Sudan'),('SR','Suriname'),('SJ','Svalbard and Jan Mayen'),('SZ','Swaziland'),('SE','Sweden'),('CH','Switzerland'),('SY','Syrian Arab Republic'),('TW','Taiwan'),('TJ','Tajikistan'),('TZ','Tanzania, United Republic of'),('TH','Thailand'),('TL','Timor-Leste'),('TG','Togo'),('TK','Tokelau'),('TO','Tonga'),('TT','Trinidad and Tobago'),('TN','Tunisia'),('TR','Turkey'),('TM','Turkmenistan'),('TC','Turks and Caicos Islands'),('TV','Tuvalu'),('UG','Uganda'),('UA','Ukraine'),('AE','United Arab Emirates'),('GB','United Kingdom'),('US','United States'),('UM','United States Minor Outlying Islands'),('UY','Uruguay'),('UZ','Uzbekistan'),('VU','Vanuatu'),('VE','Venezuela'),('VN','Viet Nam'),('VG','Virgin Islands, British'),('VI','Virgin Islands, U.s.'),('WF','Wallis and Futuna'),('EH','Western Sahara'),('YE','Yemen'),('ZM','Zambia'),('ZW','Zimbabwe'),('BQ','Bonaire, Saint Eustatius And Saba'),('CW','Cura&#x00E7;ao'),('GG','Guernsey'),('IM','Isle Of Man'),('JE','Jersey'),('ME','Montenegro'),('BL','Saint Barth&#x00E9;lemy'),('MF','Saint Martin (French Part)'),('SX','Sint Maarten (Dutch Part)'),('XX','Other / Stateless');
/*!40000 ALTER TABLE `countries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dictionary`
--

DROP TABLE IF EXISTS `dictionary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dictionary` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tag` varchar(100) NOT NULL,
  `used` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag` (`tag`)
) ENGINE=MyISAM AUTO_INCREMENT=11800 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dictionary`
--

LOCK TABLES `dictionary` WRITE;
/*!40000 ALTER TABLE `dictionary` DISABLE KEYS */;
/*!40000 ALTER TABLE `dictionary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_limit`
--

DROP TABLE IF EXISTS `email_limit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_limit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hourly_limit` int NOT NULL,
  `remaining` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_limit`
--

LOCK TABLES `email_limit` WRITE;
/*!40000 ALTER TABLE `email_limit` DISABLE KEYS */;
INSERT INTO `email_limit` VALUES (1,200,0);
/*!40000 ALTER TABLE `email_limit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_queue`
--

DROP TABLE IF EXISTS `email_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_queue` (
  `id` int NOT NULL AUTO_INCREMENT,
  `account` varchar(100) NOT NULL,
  `from_email` varchar(250) NOT NULL,
  `to_email` varchar(250) NOT NULL,
  `bcc` varchar(250) NOT NULL,
  `subject` varchar(250) NOT NULL,
  `text` text NOT NULL,
  `html` text NOT NULL,
  `sent` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_queue`
--

LOCK TABLES `email_queue` WRITE;
/*!40000 ALTER TABLE `email_queue` DISABLE KEYS */;
/*!40000 ALTER TABLE `email_queue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interactions`
--

DROP TABLE IF EXISTS `interactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'comment',
  `actor_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `object_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `object_id` int NOT NULL,
  `thread` int NOT NULL DEFAULT '0',
  `comment` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `timestamp` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=11040 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interactions`
--

LOCK TABLES `interactions` WRITE;
/*!40000 ALTER TABLE `interactions` DISABLE KEYS */;
/*!40000 ALTER TABLE `interactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `languages`
--

DROP TABLE IF EXISTS `languages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `languages` (
  `id` smallint NOT NULL AUTO_INCREMENT,
  `language` char(49) DEFAULT NULL,
  `native` varchar(100) NOT NULL,
  `iso` char(10) DEFAULT NULL,
  `available` tinyint(1) NOT NULL,
  `locked` tinyint(1) NOT NULL,
  `rtl` tinyint(1) NOT NULL,
  `admin` varchar(100) NOT NULL,
  `video1` varchar(100) NOT NULL,
  `itoe_available` tinyint NOT NULL,
  `timestamp` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=140 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `languages`
--

LOCK TABLES `languages` WRITE;
/*!40000 ALTER TABLE `languages` DISABLE KEYS */;
INSERT INTO `languages` VALUES (1,'English','English','en',1,1,0,'','rvDKTRgoSS8',1,'1512046565'),(2,'Afar','Afaraf','aa',0,0,0,'','',0,''),(3,'Abkhazian','Аҧсуа','ab',0,0,0,'','',0,''),(4,'Afrikaans','Afrikaans','af',0,0,0,'','',0,''),(5,'Amharic','አማርኛ','am',0,0,0,'','',0,''),(6,'Arabic','العربية','ar',1,0,1,'','',0,'1504645532'),(7,'Assamese','অসমীয়া','as',0,0,0,'','',0,''),(8,'Aymara','aymar aru','ay',0,0,0,'','',0,''),(9,'Azerbaijani','azərbaycan dili','az',0,0,0,'','',0,''),(10,'Bashkir','башҡорт теле','ba',0,0,0,'','',0,''),(11,'Byelorussian','Беларуская','be',0,0,0,'','',0,''),(12,'Bulgarian','български език','bg',1,0,0,'bg.admin@freeworldcharter.org','',0,'1504645616'),(13,'Bihari','भोजपुरी','bh',0,0,0,'','',0,''),(14,'Bislama','Bislama','bi',0,0,0,'','',0,''),(15,'Bengali/Bangla','বাংলা','bn',0,0,0,'','',0,''),(16,'Tibetan','བོད་ཡིག','bo',0,0,0,'','',0,''),(17,'Breton','brezhoneg','br',0,0,0,'','',0,''),(18,'Catalan','Català','ca',0,0,0,'','',0,''),(19,'Corsican','corsu, lingua corsa','co',0,0,0,'','',0,''),(20,'Czech','česky, čeština','cs',1,0,0,'cs.admin@freeworldcharter.org','vWuHFnF5AHo',1,'1550220994'),(21,'Welsh','Cymraeg','cy',0,0,0,'','',0,''),(22,'Danish','dansk','da',0,0,0,'','',0,''),(23,'German','Deutsch','de',1,0,0,'de.admin@freeworldcharter.org','UrWALc-LrVg',1,'1504645995'),(24,'Bhutani','རྫོང་ཁ','dz',0,0,0,'','',0,''),(25,'Greek','Ελληνικά','el',1,0,0,'info@feelmorethanfine.eu','',0,'1458890144'),(26,'Esperanto','Esperanto','eo',0,0,0,'','',0,''),(27,'Spanish','español, castellano','es',1,0,0,'es.admin@freeworldcharter.org','yu22JAzImik',1,'1504646464'),(28,'Estonian','eesti, eesti keel','et',0,0,0,'','',0,''),(29,'Basque','euskara, euskera','eu',0,0,0,'','',0,''),(30,'Persian','فارسی','fa',0,0,1,'','',0,''),(31,'Finnish','suomi, suomen kieli','fi',0,0,0,'','',0,''),(32,'Fiji','vosa Vakaviti','fj',0,0,0,'','',0,''),(33,'Faeroese','føroyskt','fo',0,0,0,'','',0,''),(34,'French','français, langue française','fr',1,0,0,'rafi.alla@live.ca','ORUrpuoTBOo',1,'1504645906'),(35,'Frisian','Frysk','fy',0,0,0,'','',0,''),(36,'Irish','Gaeilge','ga',0,0,0,'','',0,''),(37,'Scots/Gaelic','Gàidhlig','gd',0,0,0,'','',0,''),(38,'Galician','Galego','gl',0,0,0,'','',0,''),(39,'Guarani','Avañe\'ẽ','gn',0,0,0,'','',0,''),(40,'Gujarati','ગુજરાતી','gu',0,0,0,'','',0,''),(41,'Hausa','Hausa, هَوُسَ','ha',0,0,1,'','',0,''),(42,'Hindi','हिन्दी, हिंदी','hi',0,0,0,'','',0,''),(43,'Croatian','hrvatski','hr',1,0,0,'','',0,'1504645788'),(44,'Hungarian','Magyar','hu',0,0,0,'','',0,''),(45,'Armenian','Հայերեն','hy',0,0,0,'','',0,''),(46,'Interlingua','Interlingua','ia',0,0,0,'','',0,''),(47,'Interlingue','Interlingue','ie',0,0,0,'','',0,''),(48,'Inupiak','Iñupiaq, Iñupiatun','ik',0,0,0,'','',0,''),(49,'Indonesian','Bahasa Indonesia','in',0,0,0,'','',0,''),(50,'Icelandic','Íslenska','is',0,0,0,'','',0,''),(51,'Italian','Italiano','it',1,0,0,'it.admin@freeworldcharter.org','DK5a1q1OZyA',0,'1504646091'),(52,'Hebrew','עברית','he',1,0,1,'he.admin@freeworldcharter.org','',0,'1504646051'),(53,'Japanese','日本語 (にほんご／にっぽんご)','ja',1,0,0,'','',0,'1504646127'),(55,'Javanese','Basa Jawa','jw',0,0,0,'','',0,''),(56,'Georgian','ქართული','ka',1,0,0,'','',0,'1504645949'),(57,'Kazakh','Қазақ тілі','kk',0,0,0,'','',0,''),(58,'Greenlandic','kalaallisut, kalaallit oqaasii','kl',0,0,0,'','',0,''),(59,'Cambodian','ភាសាខ្មែរ','km',0,0,0,'','',0,''),(60,'Kannada','ಕನ್ನಡ','kn',0,0,0,'','',0,''),(61,'Korean','한국어 (韓國語), 조선말 (朝鮮語)','ko',0,0,0,'','',0,''),(62,'Kashmiri','कश्मीरी, كشميري‎','ks',0,0,0,'','',0,''),(63,'Kurdish','Kurdî, كوردی‎','ku',0,0,0,'','',0,''),(64,'Kirghiz','кыргыз тили','ky',0,0,0,'','',0,''),(65,'Latin','latine, lingua latina','la',0,0,0,'','',0,''),(66,'Lingala','Lingála','ln',0,0,0,'','',0,''),(67,'Laothian','ພາສາລາວ','lo',0,0,0,'','',0,''),(68,'Lithuanian','lietuvių kalba','lt',0,0,0,'','',0,''),(69,'Latvian/Lettish','latviešu valoda','lv',0,0,0,'','',0,''),(70,'Malagasy','Malagasy fiteny','mg',0,0,0,'','',0,''),(71,'Maori','te reo Māori','mi',0,0,0,'','',0,''),(72,'Macedonian','македонски јазик','mk',0,0,0,'','',0,''),(73,'Malayalam','മലയാളം','ml',0,0,0,'','',0,''),(74,'Mongolian','Монгол','mn',0,0,0,'','',0,''),(75,'Moldavian','лимба молдовеняскэ','mo',0,0,0,'','',0,''),(76,'Marathi','मराठी','mr',0,0,0,'','',0,''),(77,'Malay','bahasa Melayu, بهاس ملايو‎','ms',1,0,0,'','',0,'1518070662'),(78,'Maltese','Malti','mt',0,0,0,'','',0,''),(79,'Burmese','ဗမာစာ','my',0,0,0,'','',0,''),(80,'Nauru','Ekakairũ Naoero','na',0,0,0,'','',0,''),(81,'Nepali','नेपाली','ne',0,0,0,'','',0,''),(82,'Dutch','Nederlands, Vlaams','nl',1,0,0,'franks.msn@gmail.com','',0,'1504645856'),(83,'Norwegian','Norsk','no',1,0,0,'','',0,'1504646163'),(84,'Occitan','Occitan','oc',0,0,0,'','',0,''),(85,'(Afan)/Oromoor/Oriya','Afaan Oromoo','om',0,0,0,'','',0,''),(86,'Punjabi','ਪੰਜਾਬੀ, پنجابی‎','pa',0,0,0,'','',0,''),(87,'Polish','polski','pl',1,0,0,'pl.admin@freeworldcharter.org','',0,'1504646197'),(88,'Pashto/Pushto','پښتو','ps',0,0,1,'','',0,''),(89,'Portuguese','Português','pt',1,0,0,'pt.admin@freeworldcharter.org','RYNzJ6MIlWY',1,'1504646234'),(90,'Quechua','Runa Simi, Kichwa','qu',0,0,0,'','',0,''),(91,'Rhaeto-Romance','rumantsch grischun','rm',0,0,0,'','',0,''),(92,'Kirundi','kiRundi','rn',0,0,0,'','',0,''),(93,'Romanian','română','ro',1,0,0,'','',0,'1390086931'),(94,'Russian','Русский язык','ru',1,0,0,'ru.admin@freeworldcharter.org','',0,'1504646313'),(95,'Kinyarwanda','Ikinyarwanda','rw',0,0,0,'','',0,''),(96,'Sanskrit','संस्कृतम्','sa',0,0,0,'','',0,''),(97,'Sindhi','सिन्धी, سنڌي، سندھی‎','sd',0,0,0,'','',0,''),(98,'Sangro','yângâ tî sängö','sg',0,0,0,'','',0,''),(99,'Serbo-Croatian','Serbo-Croat','sh',0,0,0,'','',0,''),(100,'Singhalese','සිංහල','si',0,0,0,'','',0,''),(101,'Slovak','slovenčina','sk',1,0,0,'','SZH73EVQD00',0,'1504646391'),(102,'Slovenian','slovenščina','sl',1,0,0,'','',0,'1504646423'),(103,'Samoan','gagana fa\'a Samoa','sm',0,0,0,'','',0,''),(104,'Shona','chiShona','sn',0,0,0,'','',0,''),(105,'Somali','Soomaaliga, af Soomaali','so',0,0,0,'','',0,''),(106,'Albanian','Shqip','sq',0,0,0,'','',0,''),(107,'Serbian','српски језик','sr',1,0,0,'draganmouse@gmail.com','',0,'1504646347'),(108,'Siswati','SiSwati','ss',0,0,0,'','',0,''),(109,'Sesotho','Sesotho','st',0,0,0,'','',0,''),(110,'Sundanese','Basa Sunda','su',0,0,0,'','',0,''),(111,'Swedish','svenska','sv',1,0,0,'','',0,'1504646507'),(112,'Swahili','Kiswahili','sw',0,0,0,'','',0,''),(113,'Tamil','தமிழ்','ta',0,0,0,'','',0,''),(114,'Tegulu','తెలుగు','te',0,0,0,'','',0,''),(115,'Tajik','тоҷикӣ, toğikī, تاجیکی‎','tg',0,0,0,'','',0,''),(116,'Thai','ไทย','th',0,0,0,'','',0,''),(117,'Tigrinya','ትግርኛ','ti',0,0,0,'','',0,''),(118,'Turkmen','Türkmen, Түркмен','tk',0,0,0,'','',0,''),(119,'Tagalog','Wikang Tagalog, ᜏᜒᜃᜅ᜔ ᜆᜄᜎᜓᜄ᜔','tl',0,0,0,'','',0,''),(120,'Setswana','Setswana','tn',0,0,0,'','',0,''),(121,'Tonga','faka Tonga','to',0,0,0,'','',0,''),(122,'Turkish','Türkçe','tr',0,0,0,'','',0,''),(123,'Tsonga','Xitsonga','ts',0,0,0,'','',0,''),(124,'Tatar','татарча, tatarça, تاتارچا‎','tt',0,0,0,'','',0,''),(125,'Twi','Twi','tw',0,0,0,'','',0,''),(126,'Ukrainian','Українська','uk',0,0,0,'','',0,''),(127,'Urdu','اردو','ur',0,0,1,'','',0,''),(128,'Uzbek','O\'zbek, Ўзбек, أۇزبېك‎','uz',0,0,0,'','',0,''),(129,'Vietnamese','Tiếng Việt','vi',0,0,0,'','',0,''),(130,'Volapuk','Volapük','vo',0,0,0,'','',0,''),(131,'Wolof','Wollof','wo',0,0,0,'','',0,''),(132,'Xhosa','isiXhosa','xh',0,0,0,'','',0,''),(133,'Yoruba','Yorùbá','yo',0,0,0,'','',0,''),(134,'Chinese (Traditional)','官話','zh-hant',1,0,0,'','',0,'1504645747'),(135,'Zulu','isiZulu','zu',0,0,0,'','',0,''),(136,'Yiddish','ייִדיש','yi',0,0,1,'','',0,''),(138,'Chinese (Simplified)','官话','zh-hans',1,0,0,'','',0,'1504645715'),(139,'Portuguese (Brazilian)','Português do Brasil','pt-BR',1,0,0,'neonsouls@gmail.com','Y2PfRU9ZZ9E',1,'1518966460');
/*!40000 ALTER TABLE `languages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `listing_templates`
--

DROP TABLE IF EXISTS `listing_templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `listing_templates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `description` varchar(500) NOT NULL,
  `tags` varchar(250) NOT NULL,
  `category` int DEFAULT '0',
  `physical` tinyint NOT NULL COMMENT '1 - physical item',
  `uses` int NOT NULL,
  PRIMARY KEY (`id`),
  FULLTEXT KEY `title` (`title`,`description`,`tags`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `listing_templates`
--

LOCK TABLES `listing_templates` WRITE;
/*!40000 ALTER TABLE `listing_templates` DISABLE KEYS */;
INSERT INTO `listing_templates` VALUES (1,'Life advice','Happy to share some of life experience with you..','',2,0,13),(2,'Computer help','I can help you with your computer problem...','',18,0,11),(3,'Moving boxes / furniture','I can help you move furniture of heavy boxes...','',23,0,2),(4,'Lift share','I can offer you a ride somewhere...','',17,0,2),(5,'Transport of items','I can help with delivering some items for you...','',17,0,0),(6,'Surplus food','I can provide you with some of my surplus food..','',21,1,0),(7,'Old mobile phone','I have a cell phone that I don\'t need..','',37,1,0),(8,'Lend tools','I have some tools that you can borrow..','',42,1,3),(9,'Loan of professional camera','I have a professional camera you can borrow..','',16,1,1),(10,'Loan of music equipment','I have some music equipment you can borrow..','',34,1,1),(11,'Massage','I can offer you a massage..','',25,0,1),(12,'Reiki healing','I can perform some Reiki hands on healing..','',25,0,0),(13,'Hair cut','I can cut your hair..','',8,0,0),(14,'Counselling','I can offer some counselling..','',2,0,4),(15,'Free meal','I can cook you a meal..','',21,1,1),(16,'Unused clothes','I have some unused clothes you can have..','',14,1,1),(17,'Baby clothes','I have some baby clothes you can have..','',14,1,0),(18,'Children\'s clothes','I have some children\'s clothes you can have..','',14,1,2),(19,'Baby buggy','I have a baby pram / buggy you can have..','',7,1,0),(20,'Childrens toys','I have some childrens toys you can have..','',43,1,0),(21,'Old CDs / videos','I have some old CDs and videos you can have..','',12,1,0),(22,'Computer monitor','I have an old computer monitor you are welcome to..','',16,1,0),(23,'Unused printer','I have an old printer I no longer use..','',16,1,0),(24,'Unused scanner','I have an old computer scanner I no longer use..','',16,1,0),(25,'Television','I have a spare television you are welcome to..','',44,1,0),(26,'Unwanted table','I have an old table you can have..','',26,1,0),(27,'Unwanted piece of furniture','I have an old piece of furniture I no longer need..','',26,1,0),(28,'Computer mouse / keyboard','I have a spare computer mouse or keyboard you can have..','',16,1,0),(29,'Exercise equipment','I have some exercising equipment I no longer use..','',25,1,0),(30,'Stationary supplies','I have some office / stationary equipment that you can have..','',35,1,0),(31,'Video games','I have some video games I no longer use..','',43,1,0),(32,'Old game console','I have an old game console you are welcome to..','',43,1,0),(33,'Set of speakers','I have an old set of speakers I no longer use..','',34,1,0),(34,'Headphones / earbuds','I have an unused set of headphones / earbuds that you can have..','',34,1,0),(35,'Concrete blocks / slabs','I have some blocks or slabs that you can take..','',27,1,0),(36,'Wood','I have some good timber you can collect..','',27,1,0),(37,'Firewood','I have an excess of firewood which you are welcome to collect..','',26,1,0),(38,'Plants','I have some plants that you are welcome to..','',26,1,3),(39,'Herbs / spices','I have some herbs and spices that you can take..','',26,1,0),(40,'Vegetables','I have some fresh vegetables which you are welcome to..','',26,1,0),(41,'Seeds','I have some seeds that you can have..','',26,1,0),(42,'Wristwatch','I have a spare wristwatch that you can have..','',14,1,0),(43,'Sunglasses','I have a spare pair of sunglasses which you can have..','',14,1,1),(44,'Make-up advice','I can show you some make-up tricks..','',8,0,0),(45,'Unused make-up','I have some spare make-up I dont need..','',8,1,0),(46,'Vinyl records','I have some old vinyl records which you are welcome to..','',12,1,0),(47,'Spare land','I have some spare land which you are welcome to use..','',30,1,0),(48,'Books','I have some books you can have..','',10,1,0),(49,'Spare room','I have a spare room and you are welcome to stay..','',1,0,0),(50,'Child bike','I have a childrens bicycle which you are welcome to..','',9,1,0),(51,'Music lesson','I can give you a music or singing online or in person..','',18,0,0),(52,'Animation','I can create a short animation for you..','',46,0,0),(53,'Video editing','I can edit a video for you..','',46,0,3),(54,'Translation','I can do a translation for you..','',48,0,1),(55,'Proofreading','I can proofread some text for you..','',45,0,4),(56,'Copywriting','I can write some good copy for your project..','',45,0,0),(57,'Marketing and promotion','I can give you some advice on marketing and promotion..','',32,0,0),(58,'Share point','Local sharing point or library in my area..','',51,0,5),(59,'Community announcement','Something is happening in my area...','',15,0,0);
/*!40000 ALTER TABLE `listing_templates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `member_blocks`
--

DROP TABLE IF EXISTS `member_blocks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_blocks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `blocker_id` int NOT NULL,
  `blocked_id` int NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member_blocks`
--

LOCK TABLES `member_blocks` WRITE;
/*!40000 ALTER TABLE `member_blocks` DISABLE KEYS */;
/*!40000 ALTER TABLE `member_blocks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `members`
--

DROP TABLE IF EXISTS `members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `members` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(80) NOT NULL,
  `last_name` varchar(80) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `activated` tinyint(1) NOT NULL DEFAULT '0',
  `ac_type` tinyint(1) NOT NULL DEFAULT '1',
  `org_name` varchar(200) NOT NULL,
  `org_desc` varchar(1000) NOT NULL,
  `street` varchar(200) NOT NULL,
  `city` varchar(100) NOT NULL,
  `region` varchar(100) NOT NULL,
  `postcode` varchar(50) NOT NULL,
  `country_iso` varchar(2) NOT NULL,
  `country` varchar(100) NOT NULL,
  `lat` varchar(20) NOT NULL,
  `lon` varchar(20) NOT NULL,
  `phone` varchar(100) NOT NULL,
  `image` varchar(100) NOT NULL,
  `tags` varchar(500) NOT NULL,
  `about_me` text NOT NULL,
  `mailme` tinyint(1) NOT NULL DEFAULT '0',
  `mailme_sent` tinyint(1) NOT NULL DEFAULT '0',
  `badmail` tinyint NOT NULL DEFAULT '0' COMMENT '1 = bounced',
  `allow_contact` tinyint(1) NOT NULL DEFAULT '1',
  `matchme` tinyint(1) NOT NULL DEFAULT '1',
  `matchme_sent` tinyint(1) NOT NULL DEFAULT '0',
  `timestamp` varchar(20) NOT NULL,
  `time_date` varchar(50) NOT NULL,
  `last_active` varchar(20) NOT NULL,
  `patronage` int NOT NULL,
  `language` varchar(100) NOT NULL,
  `auto_trans` tinyint NOT NULL DEFAULT '0',
  `gifted` int NOT NULL,
  `trust_score` int NOT NULL DEFAULT '0',
  `badge_level` tinyint NOT NULL,
  `star_rating` varchar(10) NOT NULL DEFAULT '0',
  `ip` varchar(20) NOT NULL,
  `authcode` varchar(100) NOT NULL,
  `HP_id` varchar(11) NOT NULL,
  `joined` int NOT NULL,
  `is_founder` tinyint DEFAULT '0',
  `is_admin` tinyint NOT NULL,
  `gotit` int NOT NULL DEFAULT '0' COMMENT '1 = Site alert was read; 0 = not read',
  `rank` int NOT NULL DEFAULT '0',
  `session_id` varchar(50) NOT NULL,
  `note` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  FULLTEXT KEY `first_name` (`first_name`,`last_name`,`org_name`,`org_desc`,`tags`,`about_me`),
  FULLTEXT KEY `about_me` (`about_me`,`tags`)
) ENGINE=MyISAM AUTO_INCREMENT=61015 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members`
--

LOCK TABLES `members` WRITE;
/*!40000 ALTER TABLE `members` DISABLE KEYS */;
/*!40000 ALTER TABLE `members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sender` int NOT NULL,
  `recipient` int NOT NULL,
  `convo_id` varchar(20) NOT NULL,
  `message` mediumtext NOT NULL,
  `type` varchar(10) NOT NULL COMMENT 'message or alert?',
  `status` varchar(10) NOT NULL COMMENT 'sent or seen',
  `timestamp` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=61111 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `source` varchar(100) NOT NULL DEFAULT 'sharebay.org',
  `lister` int NOT NULL COMMENT 'id of lister',
  `title` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `quantity` int NOT NULL,
  `type` varchar(10) NOT NULL COMMENT 'Offer or request?',
  `physical` tinyint NOT NULL DEFAULT '0',
  `category` int NOT NULL COMMENT 'Category ID',
  `trusted_only` int NOT NULL DEFAULT '0',
  `terms` varchar(10) NOT NULL COMMENT 'free or loan',
  `image` varchar(100) NOT NULL,
  `tags` varchar(250) NOT NULL,
  `lat` varchar(20) NOT NULL,
  `lon` varchar(20) NOT NULL,
  `send_ok` tinyint DEFAULT '0',
  `status` varchar(10) NOT NULL DEFAULT 'live' COMMENT 'live, complete, pending, spam, deleted',
  `timestamp` int NOT NULL,
  `rank` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  FULLTEXT KEY `title` (`title`,`description`,`tags`)
) ENGINE=MyISAM AUTO_INCREMENT=1952 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts`
--

LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reviewer_id` int NOT NULL,
  `target_id` int NOT NULL,
  `trans_id` int NOT NULL,
  `stars` int NOT NULL COMMENT '1 to 5',
  `comment` text NOT NULL,
  `timestamp` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `searches`
--

DROP TABLE IF EXISTS `searches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `searches` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) NOT NULL DEFAULT '0',
  `query` varchar(200) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6053 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `searches`
--

LOCK TABLES `searches` WRITE;
/*!40000 ALTER TABLE `searches` DISABLE KEYS */;
/*!40000 ALTER TABLE `searches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `site_averages`
--

DROP TABLE IF EXISTS `site_averages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `site_averages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stripe_1` int NOT NULL,
  `stripe_2` int NOT NULL,
  `stripe_3` int NOT NULL,
  `offers_max` int NOT NULL,
  `gave_max` int NOT NULL,
  `got_max` int NOT NULL,
  `trust_max` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `site_averages`
--

LOCK TABLES `site_averages` WRITE;
/*!40000 ALTER TABLE `site_averages` DISABLE KEYS */;
INSERT INTO `site_averages` VALUES (1,0,0,0,0,0,0,0);
/*!40000 ALTER TABLE `site_averages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `spam_reports`
--

DROP TABLE IF EXISTS `spam_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `spam_reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `object_type` varchar(10) NOT NULL COMMENT 'Profile or listing',
  `object_id` int NOT NULL,
  `reporter_id` int NOT NULL,
  `action_taken` int NOT NULL DEFAULT '0',
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `object_type` (`object_type`,`object_id`,`reporter_id`)
) ENGINE=InnoDB AUTO_INCREMENT=75 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `spam_reports`
--

LOCK TABLES `spam_reports` WRITE;
/*!40000 ALTER TABLE `spam_reports` DISABLE KEYS */;
/*!40000 ALTER TABLE `spam_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `listing_id` int NOT NULL,
  `listing_type` varchar(10) NOT NULL COMMENT 'offer, request, [FUTURE]',
  `giver_id` int NOT NULL,
  `getter_id` int NOT NULL,
  `quantity` int NOT NULL,
  `shipping_cost` varchar(10) NOT NULL,
  `status` varchar(20) NOT NULL COMMENT 'applied, accepted, payment_requested, payment_offered, paid, sent, delivered, cancelled, auto-cancelled',
  `timestamp` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1312 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unsubscribes`
--

DROP TABLE IF EXISTS `unsubscribes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unsubscribes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `actor_id` int NOT NULL,
  `object_type` varchar(20) NOT NULL,
  `object_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `actor_id` (`actor_id`,`object_type`,`object_id`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unsubscribes`
--

LOCK TABLES `unsubscribes` WRITE;
/*!40000 ALTER TABLE `unsubscribes` DISABLE KEYS */;
/*!40000 ALTER TABLE `unsubscribes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-10 18:55:31
