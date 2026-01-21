-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 30, 2025 at 03:34 PM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `price_ai_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `alerts`
--

CREATE TABLE `alerts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_hash` varchar(1024) NOT NULL,
  `product_name` text DEFAULT NULL,
  `target_price` decimal(12,2) NOT NULL,
  `current_price` decimal(12,2) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `notified` tinyint(1) DEFAULT 0,
  `notified_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `alerts`
--

INSERT INTO `alerts` (`id`, `user_id`, `product_hash`, `product_name`, `target_price`, `current_price`, `created_at`, `notified`, `notified_at`) VALUES
(1, 1, 'https://www.amazon.in/Lymio-Cargo-Cotton-Cargos-Cargo-67-Grey-XL/dp/B0DF7C14W1/ref=sr_1_115?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.XK9vFrN9WsmzvPCbS25EM686rz7AKaOEgR8HjGyvl73ukrun7nkdjSbmWXUHSinOKfFrMucPJ-z83Ku5TuPe1JiMF_MZoK6sbkYG60UWZnUzRuRcp0hLDC9CPU8MsgpopxaU9opdliEPp1nmHmNdFkP-7L0OHnybTckE9UL4YNbHlBQzx_m290qcvlfXCdxUy1sBNJx3CSHpngeZpr8fXDctgapPwe7TWGj4UEb0P9j3f8HTr_a3PfUDx6zQDs-9jgsiUDDqIyNQSG-zIg-wH1cHrwygiZjp9LU6cFLyW1U.YxJ2MY84EMKHUQGsrwe2nGxAgYbe2iIbW7IaXi_pN2c&dib_tag=se&keywords=men+fashion+clothes&qid=1764906920&sprefix=men+fashion%2Caps%2C271&sr=8-115&xpid=-m7_BlYD0bePS', 'men cargo || men cargo pants || men cargo pants cotton || cargos for men (cargo-66-69)', '780.00', NULL, '2025-12-30 10:34:46', 0, NULL),
(2, 1, 'https://www.amazon.in/TOPLOT-Cargo-Trousers-Utility-Men-Camo-Cargo-5236-GreY-30/dp/B0F13N46YQ/ref=sr_1_60?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.4zLtjumoTyBkoo_ZFXzl1eeSHIRVHRTd5g0CxtTpR8mIlNVqVLn_oKXAecr6wMmc02SuhwsKWzs354qINp9riSkFnVWGZWzxo1dEzQvQApdqmsaO5BwLcFz7XrGWqxG0-zr9nso9fcWYuebkjE25WQaOZ7xCzCDUIoJS2AkEWZ2sH_1oJx2dbGpccECfFYlTapvFVB-71nv_LDE6nu0z9euT8u1pLo7jSGs-yoJwNyZGtZL7pjfuNscgEQC2Hy60JduSHV3DSUVG9kEk2PCctfNHJkuEYntFrVD695QhwZY.PMfRphZGABjJchQtMIClMyoh2ehI_DwbwVMxFhwqCmk&dib_tag=se&keywords=men+fashion+clothes&qid=1764906879&sprefix=men+fashion%2Caps%2C271&sr=8-60&xpid=-m7_BlYD0bePS', 'men cargo || men cargo pants ||camo trousers || utility pants (5236)', '600.00', NULL, '2025-12-30 12:11:01', 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `price_history`
--

CREATE TABLE `price_history` (
  `history_id` int(11) NOT NULL,
  `product_hash` varchar(1000) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `price_source` varchar(100) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `price_history`
--

INSERT INTO `price_history` (`history_id`, `product_hash`, `price`, `price_source`, `timestamp`) VALUES
(1, 'https://www.flipkart.com/google-pixel-7-lemongrass-128-gb/p/itm45d75002be0e7?pid=MOBGHW44ZSN5EPGU&lid=LSTMOBGHW44ZSN5EPGUVDQE3A&marketplace=FLIPKART&store=tyy%2F4io&srno=b_40_945&otracker=CLP_Filters&fm=organic&iid=ae74e364-0bed-4954-9a9f-aadb1915d37b.MOBGHW44ZSN5EPGU.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '30999.00', 'Flipkart', '2025-12-16 20:43:28'),
(2, 'https://www.flipkart.com/google-pixel-10-pro-xl-jade-256-gb/p/itm702fa25db1f13?pid=MOBHEXHRPRFQZE8H&lid=LSTMOBHEXHRPRFQZE8HBPV23X&marketplace=FLIPKART&store=tyy%2F4io&srno=b_2_37&otracker=CLP_Filters&fm=organic&iid=en_0FW4mGMItYmDEUsQsi0n9RT_r_VBoWGUd6JmCPkhwLlhkSShVPVFX4-AstoUbGshjBCgx2o-ncYrelKw5DjYzPUFjCTyOHoHZs-Z5_PS_w0%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '124999.00', 'Flipkart', '2025-12-16 20:43:57'),
(3, 'https://www.flipkart.com/google-pixel-10-pro-xl-jade-256-gb/p/itm702fa25db1f13?pid=MOBHEXHRPRFQZE8H&lid=LSTMOBHEXHRPRFQZE8HBPV23X&marketplace=FLIPKART&store=tyy%2F4io&srno=b_1_17&otracker=CLP_Filters&fm=organic&iid=en_vJOdJfY9G2n9Inre9WnUksU3FQK0ApxmXDVJaXevIdMxKwTJSMgZUlpUgYs6xnqp6FLwgjf1a1cvxqOcvULRTevN4Mn-dv-pi277bRzMbnY%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '124999.00', 'Flipkart', '2025-12-16 20:44:28'),
(4, 'https://www.flipkart.com/google-pixel-10-pro-jade-256-gb/p/itm56ea5d61cab29?pid=MOBHEXHRYASTHFKT&lid=LSTMOBHEXHRYASTHFKTIOACBA&marketplace=FLIPKART&store=tyy%2F4io&srno=b_1_11&otracker=CLP_Filters&fm=organic&iid=en_vJOdJfY9G2n9Inre9WnUksU3FQK0ApxmXDVJaXevIdOLttBrOV77z93LY9_--pZi7p-4NYMGbiFZQMfqlwznD4QEIsITtCzc4bHaOMTqL08%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '109999.00', 'Flipkart', '2025-12-16 20:45:08'),
(5, 'https://www.flipkart.com/google-pixel-7-lemongrass-128-gb/p/itm45d75002be0e7?pid=MOBGHW44ZSN5EPGU&lid=LSTMOBGHW44ZSN5EPGUVDQE3A&marketplace=FLIPKART&store=tyy%2F4io&srno=b_40_945&otracker=CLP_Filters&fm=organic&iid=ae74e364-0bed-4954-9a9f-aadb1915d37b.MOBGHW44ZSN5EPGU.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '30999.00', 'Flipkart', '2025-12-16 20:47:54'),
(6, 'https://www.flipkart.com/google-pixel-10-pro-xl-jade-256-gb/p/itm702fa25db1f13?pid=MOBHEXHRPRFQZE8H&lid=LSTMOBHEXHRPRFQZE8HBPV23X&marketplace=FLIPKART&store=tyy%2F4io&srno=b_2_37&otracker=CLP_Filters&fm=organic&iid=en_0FW4mGMItYmDEUsQsi0n9RT_r_VBoWGUd6JmCPkhwLlhkSShVPVFX4-AstoUbGshjBCgx2o-ncYrelKw5DjYzPUFjCTyOHoHZs-Z5_PS_w0%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '124999.00', 'Flipkart', '2025-12-16 20:53:47'),
(7, 'https://www.flipkart.com/google-pixel-7-lemongrass-128-gb/p/itm45d75002be0e7?pid=MOBGHW44ZSN5EPGU&lid=LSTMOBGHW44ZSN5EPGUVDQE3A&marketplace=FLIPKART&store=tyy%2F4io&srno=b_40_945&otracker=CLP_Filters&fm=organic&iid=ae74e364-0bed-4954-9a9f-aadb1915d37b.MOBGHW44ZSN5EPGU.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '30999.00', 'Flipkart', '2025-12-16 21:06:19'),
(8, 'https://www.flipkart.com/google-pixel-7-lemongrass-128-gb/p/itm45d75002be0e7?pid=MOBGHW44ZSN5EPGU&lid=LSTMOBGHW44ZSN5EPGUVDQE3A&marketplace=FLIPKART&store=tyy%2F4io&srno=b_40_945&otracker=CLP_Filters&fm=organic&iid=ae74e364-0bed-4954-9a9f-aadb1915d37b.MOBGHW44ZSN5EPGU.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '30999.00', 'Flipkart', '2025-12-16 21:09:30'),
(9, 'https://www.flipkart.com/google-pixel-10-lemongrass-256-gb/p/itmb9d9694811d2e?pid=MOBHEXHRGZ3WMHNS&lid=LSTMOBHEXHRGZ3WMHNSYMLO3G&marketplace=FLIPKART&store=tyy%2F4io&srno=b_7_150&otracker=CLP_Filters&fm=organic&iid=b17b03dd-1866-49a0-a5ab-cdc27ad49aae.MOBHEXHRGZ3WMHNS.SEARCH&ppt=browse&ppn=browse&ssid=nv337feq800000001764861750489', '79999.00', 'Flipkart', '2025-12-16 21:09:48'),
(10, 'https://www.flipkart.com/google-pixel-7-lemongrass-128-gb/p/itm45d75002be0e7?pid=MOBGHW44ZSN5EPGU&lid=LSTMOBGHW44ZSN5EPGUVDQE3A&marketplace=FLIPKART&store=tyy%2F4io&srno=b_40_945&otracker=CLP_Filters&fm=organic&iid=ae74e364-0bed-4954-9a9f-aadb1915d37b.MOBGHW44ZSN5EPGU.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '30999.00', 'Flipkart', '2025-12-16 21:19:20'),
(11, 'https://www.flipkart.com/google-pixel-10-pro-porcelain-256-gb/p/itmb41080c79ef00?pid=MOBHEXHRMGFJ93DM&lid=LSTMOBHEXHRMGFJ93DMPLAAAK&marketplace=FLIPKART&store=tyy%2F4io&srno=b_23_530&otracker=CLP_Filters&fm=organic&iid=45d6fb3b-3479-471b-85b3-01ff75e93ff5.MOBHEXHRMGFJ93DM.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '109999.00', 'Flipkart', '2025-12-16 21:19:51'),
(12, 'https://www.flipkart.com/google-pixel-10-pro-xl-jade-256-gb/p/itm702fa25db1f13?pid=MOBHEXHRPRFQZE8H&lid=LSTMOBHEXHRPRFQZE8HBPV23X&marketplace=FLIPKART&store=tyy%2F4io&srno=b_2_37&otracker=CLP_Filters&fm=organic&iid=en_0FW4mGMItYmDEUsQsi0n9RT_r_VBoWGUd6JmCPkhwLlhkSShVPVFX4-AstoUbGshjBCgx2o-ncYrelKw5DjYzPUFjCTyOHoHZs-Z5_PS_w0%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '124999.00', 'Flipkart', '2025-12-16 21:55:38'),
(13, 'https://www.flipkart.com/google-pixel-7-lemongrass-128-gb/p/itm45d75002be0e7?pid=MOBGHW44ZSN5EPGU&lid=LSTMOBGHW44ZSN5EPGUVDQE3A&marketplace=FLIPKART&store=tyy%2F4io&srno=b_40_945&otracker=CLP_Filters&fm=organic&iid=ae74e364-0bed-4954-9a9f-aadb1915d37b.MOBGHW44ZSN5EPGU.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '30999.00', 'Flipkart', '2025-12-19 11:19:37'),
(14, 'https://www.amazon.in/Allen-Solly-Geometric-Regular-ASSFWMOFI31587_White_42/dp/B07DMVHSQ1/ref=sr_1_40?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.bYIURbUF8gj_S5PXtkQXGYM7ptVlq4lp8ZLgZ4ovAQ_2Ign4VGh5OQ2E4OuLGswFxiDVgSuF6mdajYGkGCRP13k20i0Ygl5wmroB0eYmdpCJ2n5Dg3MkjWtDbWvDLtw8k5vTnp-X5Phdzm12t2O2R6cftyGn_FallehHrwOSMMios0KQ-Jmy6STPZ_N6E2v9XK9gyjRzxJTQ1Q80rGToh_chLmBq6nCMSnwmeVy89ks6mntxDa3O2w2C-R019rjpQSmDWQhwsPEstoZmVi6u_7FGvvTdxs0__rRN--5MuDg.Bt_w-ob_fdo94Gv4bWPiomI5GULI1VkAlmvNU0xg99I&dib_tag=se&keywords=men+fashion+clothes&qid=1764906841&sprefix=men+fashion%2Caps%2C271&sr=8-40', '749.00', 'Amazon', '2025-12-19 11:21:30'),
(15, 'https://www.amazon.in/Lymio-Regular-Shirt-Stylish-Resort-Slub/dp/B0DZCVHK27/ref=sr_1_35?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.bYIURbUF8gj_S5PXtkQXGYM7ptVlq4lp8ZLgZ4ovAQ_2Ign4VGh5OQ2E4OuLGswFxiDVgSuF6mdajYGkGCRP13k20i0Ygl5wmroB0eYmdpCJ2n5Dg3MkjWtDbWvDLtw8k5vTnp-X5Phdzm12t2O2R6cftyGn_FallehHrwOSMMios0KQ-Jmy6STPZ_N6E2v9XK9gyjRzxJTQ1Q80rGToh_chLmBq6nCMSnwmeVy89ks6mntxDa3O2w2C-R019rjpQSmDWQhwsPEstoZmVi6u_7FGvvTdxs0__rRN--5MuDg.Bt_w-ob_fdo94Gv4bWPiomI5GULI1VkAlmvNU0xg99I&dib_tag=se&keywords=men+fashion+clothes&qid=1764906841&sprefix=men+fashion%2Caps%2C271&sr=8-35', '419.00', 'Amazon', '2025-12-19 11:21:34'),
(16, 'https://www.flipkart.com/google-pixel-10-lemongrass-256-gb/p/itmb9d9694811d2e?pid=MOBHEXHRGZ3WMHNS&lid=LSTMOBHEXHRGZ3WMHNSYMLO3G&marketplace=FLIPKART&store=tyy%2F4io&srno=b_7_150&otracker=CLP_Filters&fm=organic&iid=b17b03dd-1866-49a0-a5ab-cdc27ad49aae.MOBHEXHRGZ3WMHNS.SEARCH&ppt=browse&ppn=browse&ssid=nv337feq800000001764861750489', '79999.00', 'Flipkart', '2025-12-19 12:22:47'),
(17, 'https://www.flipkart.com/google-pixel-7-lemongrass-128-gb/p/itm45d75002be0e7?pid=MOBGHW44ZSN5EPGU&lid=LSTMOBGHW44ZSN5EPGUVDQE3A&marketplace=FLIPKART&store=tyy%2F4io&srno=b_40_945&otracker=CLP_Filters&fm=organic&iid=ae74e364-0bed-4954-9a9f-aadb1915d37b.MOBGHW44ZSN5EPGU.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '30999.00', 'Flipkart', '2025-12-20 20:48:04'),
(18, 'https://www.flipkart.com/google-pixel-10-pro-jade-256-gb/p/itm56ea5d61cab29?pid=MOBHEXHRYASTHFKT&lid=LSTMOBHEXHRYASTHFKTIOACBA&marketplace=FLIPKART&store=tyy%2F4io&srno=b_2_32&otracker=CLP_Filters&fm=organic&iid=en_0FW4mGMItYmDEUsQsi0n9RT_r_VBoWGUd6JmCPkhwLmNEOj6Z5krJUBKXj4dW-CmOzOIsqGbAMLFtiDJD5SLRg%3D%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '109999.00', 'Flipkart', '2025-12-20 20:49:02'),
(19, 'https://www.flipkart.com/google-pixel-10-pro-jade-256-gb/p/itm56ea5d61cab29?pid=MOBHEXHRYASTHFKT&lid=LSTMOBHEXHRYASTHFKTIOACBA&marketplace=FLIPKART&store=tyy%2F4io&srno=b_1_11&otracker=CLP_Filters&fm=organic&iid=en_vJOdJfY9G2n9Inre9WnUksU3FQK0ApxmXDVJaXevIdOLttBrOV77z93LY9_--pZi7p-4NYMGbiFZQMfqlwznD4QEIsITtCzc4bHaOMTqL08%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '109999.00', 'Flipkart', '2025-12-20 20:49:46'),
(20, 'https://www.flipkart.com/google-pixel-7a-coral-128-gb/p/itmb4d7b100b1a4d?pid=MOBGT5F26QJYZUZS&lid=LSTMOBGT5F26QJYZUZSUUTWOI&marketplace=FLIPKART&store=tyy%2F4io&srno=b_26_616&otracker=CLP_Filters&fm=organic&iid=2400bfa7-6aab-4554-8dac-26e0c81d4eca.MOBGT5F26QJYZUZS.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '28999.00', 'Flipkart', '2025-12-24 09:03:11'),
(21, 'https://www.amazon.in/AWG-ALL-WEATHER-GEAR-Windcheater/dp/B0FTVHXSRX/ref=sr_1_219?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.Fm0MWebXZADrW6_KFAV4Czl2mW4troaQrCEIiMN6ncq_CeFTVzuV7390DvqGR1D1627vqdpqKsgyH3MLHTYz_ew-PZd2PxR-i5NIK5Q9kkleZ_xQLqgxJIgBC9J--Cy2gdRS8ICKydRn5sM6aoGW0L01eXG-yLhjM9sVC6wJK-X_FrzxyRsFKTWBUbzepabPJfi1NOEDgPRL8OKm9E0PoLN-Vpp8x0eW7FFaT27Qh2maWNEkQYxqAspCDvwDkrK1h7XbFh02lwZDmH9qu6hckgJqcQEgUpDMOa-LetDvpfY.FABnphS1CupA8-HFbqZHO-ChaDV9QOSzz-a96U7giNU&dib_tag=se&keywords=men+fashion+clothes&qid=1764907092&sprefix=men+fashion%2Caps%2C271&sr=8-219&xpid=-m7_BlYD0bePS', '929.00', 'Amazon', '2025-12-24 10:27:16'),
(22, 'https://www.amazon.in/Lymio-Jackets-Lightweight-Outwear-J-9-Grey-XL/dp/B0FK9JPFYP/ref=sr_1_10?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.bYIURbUF8gj_S5PXtkQXGYM7ptVlq4lp8ZLgZ4ovAQ_2Ign4VGh5OQ2E4OuLGswFxiDVgSuF6mdajYGkGCRP13k20i0Ygl5wmroB0eYmdpCJ2n5Dg3MkjWtDbWvDLtw8k5vTnp-X5Phdzm12t2O2R6cftyGn_FallehHrwOSMMios0KQ-Jmy6STPZ_N6E2v9XK9gyjRzxJTQ1Q80rGToh_chLmBq6nCMSnwmeVy89ks6mntxDa3O2w2C-R019rjpQSmDWQhwsPEstoZmVi6u_7FGvvTdxs0__rRN--5MuDg.Bt_w-ob_fdo94Gv4bWPiomI5GULI1VkAlmvNU0xg99I&dib_tag=se&keywords=men+fashion+clothes&qid=1764906841&sprefix=men+fashion%2Caps%2C271&sr=8-10', '703.00', 'Amazon', '2025-12-24 10:27:22'),
(23, 'https://www.amazon.in/sspa/click?ie=UTF8&spc=MToyMTMwNTQ3MDg0MzU0NjM4OjE3NjQ5MDY5MjE6c3BfYXRmX25leHQ6MzAwNzg0NjM2NTUzNTMyOjowOjo&url=%2FBoldfit-Polyester-Sweatshirt-Bftbm4022S-Bkxxl_Black%2Fdp%2FB0DKNXF3N3%2Fref%3Dsr_1_97_sspa%3Fcrid%3D28H7076H9RSND%26dib%3DeyJ2IjoiMSJ9.AH0p9K-bR6tBnJMQ_twf7QAMr2MHsmEQHwLBr6sIJEzGv4VJ3fP5aUmNeGTmavUOX2dAdd35a6zX5t5eoeGP5lUJuBb6hBSnUNj5jFAyI3c.uOlRsvy2jClD__V8kGbdqvrX4-EPbdMlMWoNx6pbTz4%26dib_tag%3Dse%26keywords%3Dmen%2Bfashion%2Bclothes%26qid%3D1764906920%26sprefix%3Dmen%2Bfashion%252Caps%252C271%26sr%3D8-97-spons%26xpid%3D-m7_BlYD0bePS%26aref%3DPWUUyMKpDu%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGZfbmV4dA%26psc%3D1&aref=PWUUyMKpDu&sp_cr=ZAZ', '799.00', 'Amazon', '2025-12-27 09:00:36'),
(24, 'https://www.amazon.in/Allen-Solly-Geometric-Regular-ASSFWMOFI31587_White_42/dp/B07DMVHSQ1/ref=sr_1_40?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.bYIURbUF8gj_S5PXtkQXGYM7ptVlq4lp8ZLgZ4ovAQ_2Ign4VGh5OQ2E4OuLGswFxiDVgSuF6mdajYGkGCRP13k20i0Ygl5wmroB0eYmdpCJ2n5Dg3MkjWtDbWvDLtw8k5vTnp-X5Phdzm12t2O2R6cftyGn_FallehHrwOSMMios0KQ-Jmy6STPZ_N6E2v9XK9gyjRzxJTQ1Q80rGToh_chLmBq6nCMSnwmeVy89ks6mntxDa3O2w2C-R019rjpQSmDWQhwsPEstoZmVi6u_7FGvvTdxs0__rRN--5MuDg.Bt_w-ob_fdo94Gv4bWPiomI5GULI1VkAlmvNU0xg99I&dib_tag=se&keywords=men+fashion+clothes&qid=1764906841&sprefix=men+fashion%2Caps%2C271&sr=8-40', '749.00', 'Amazon', '2025-12-27 09:02:57'),
(25, 'https://www.amazon.in/Puma-Dazzler-Peacoat-High-Red-PUMA-Sneaker/dp/B09XXL9D7K/ref=sr_1_27?crid=3RHED1UY34ZEC&dib=eyJ2IjoiMSJ9.yJWiNZUqAyKcgoyahgIhhE7gtA0BNJQfjFHBOlZEn6qmZsBwomYibmWAg7_L6UJiW-RdbF1TKJiU2wscrSMTyoDP3e376uJlzoh1l27kGbGZYhdAWFqgJycAvG20Bwlq5SwGueaWMLSu9xhhWiwGEVJPmStNqGoL4qC7_b-7_F72uaLjhhbGsnppForErfIrTWkQ4twYQcfXK9I4bzqeGxzuaOiUWm39lSzWP_y3jV1u6_kcfLRCYQylsuS39MSaUmXP66xUMVXC0KxeYj7WyKZHwXSarWb5Sm7I-O2JQtk.Pvdo0mMbqM66LJgK19V-Ntvz4hxyevvzdZkrtNIhgvI&dib_tag=se&keywords=shoes&qid=1764679369&sprefix=shoes%2Caps%2C465&sr=8-27', '1099.00', 'Amazon', '2025-12-27 10:03:38'),
(26, 'https://www.amazon.in/BULLMER-Clothing-Trendy-Shirt-Co-ords/dp/B0D1CG56ND/ref=sr_1_141?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.XK9vFrN9WsmzvPCbS25EM686rz7AKaOEgR8HjGyvl73ukrun7nkdjSbmWXUHSinOKfFrMucPJ-z83Ku5TuPe1JiMF_MZoK6sbkYG60UWZnUzRuRcp0hLDC9CPU8MsgpopxaU9opdliEPp1nmHmNdFkP-7L0OHnybTckE9UL4YNbHlBQzx_m290qcvlfXCdxUy1sBNJx3CSHpngeZpr8fXDctgapPwe7TWGj4UEb0P9j3f8HTr_a3PfUDx6zQDs-9jgsiUDDqIyNQSG-zIg-wH1cHrwygiZjp9LU6cFLyW1U.YxJ2MY84EMKHUQGsrwe2nGxAgYbe2iIbW7IaXi_pN2c&dib_tag=se&keywords=men+fashion+clothes&qid=1764906920&sprefix=men+fashion%2Caps%2C271&sr=8-141&xpid=-m7_BlYD0bePS', '778.00', 'Amazon', '2025-12-27 10:18:00'),
(27, 'https://www.flipkart.com/vivo-y18t-gem-green-128-gb/p/itme070e0d6f5af3?pid=MOBH5VZZYVAK5DEK&lid=LSTMOBH5VZZYVAK5DEKP89HYU&marketplace=FLIPKART&store=tyy%2F4io&srno=b_30_697&otracker=CLP_Filters&fm=organic&iid=530060d2-858c-498c-b482-6fbf9ded2032.MOBH5VZZYVAK5DEK.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', '8499.00', 'Flipkart', '2025-12-27 11:23:24');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `registration_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `full_name`, `email`, `password_hash`, `registration_date`) VALUES
(1, 'kavya', 'adminkavya@example.com', 'scrypt:32768:8:1$wZyf0VmlC2Ncuq74$50ecc965bdf11af5dfc3553fcaf9054f165c83713a8eadad20aaed20bfe8b925bed0179b7155e7120597a2b020043f84b6c76f94ca46cfdf3cf9a052f68d4bc0', '2025-12-12 18:16:04'),
(2, 'jenitha', 'jenitha@gmail.com', 'scrypt:32768:8:1$tJBc0xRw6caeExH8$e1669c4ab0baca82aa0bc1a63a063b697dfbbd80ce06133b2ba40c073a8c028533112cdc06a9f478ca01441af73b45691f76fc0e9f1d0001f2a4897e9d90ea46', '2025-12-13 04:04:00'),
(3, 'Shivani', 'shivani@gmail.com', 'scrypt:32768:8:1$0cl7HZfjGAMCYTL8$155a32149fe01f49b11f32c14ff907c5408e16497011bc484c0c8aec2e924af8ea1235f24c8771da9b27451127d2a807ea3dd40857ea69cc883059149e3b97dc', '2025-12-16 16:25:21'),
(4, 'Prajna', 'prajna@gmail.com', 'scrypt:32768:8:1$bjDICizPuSs2fAYq$1b18b6d024df1e34875fb659d303f7e1bd3a0ebe6dc37f6d4518bff4705092c304ea37cc8617b05315830d42b81ced5a9f100a379ce49e32d15480cbad97fa45', '2025-12-20 15:20:55'),
(5, 'John', 'johngmail.com', 'scrypt:32768:8:1$L6DPvCB9iVMVdEzr$317ca31bd3d0bb94e7b9614198508ba7f0fb8bdafbd65d7edd9f75b0001e9b7217e4e6bb025c883ecd4a998c1192f563c748731c487c36ceca40ee8f4bdadd34', '2025-12-20 15:21:51');

-- --------------------------------------------------------

--
-- Table structure for table `wishlist`
--

CREATE TABLE `wishlist` (
  `wishlist_id` int(11) NOT NULL,
  `user_id` int(10) UNSIGNED NOT NULL,
  `product_hash` varchar(1000) NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `current_price` decimal(10,2) NOT NULL,
  `image_src` varchar(512) DEFAULT NULL,
  `date_added` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `wishlist`
--

INSERT INTO `wishlist` (`wishlist_id`, `user_id`, `product_hash`, `product_name`, `current_price`, `image_src`, `date_added`) VALUES
(1, 1, 'https://www.flipkart.com/google-pixel-7-lemongrass-128-gb/p/itm45d75002be0e7?pid=MOBGHW44ZSN5EPGU&lid=LSTMOBGHW44ZSN5EPGUVDQE3A&marketplace=FLIPKART&store=tyy%2F4io&srno=b_40_945&otracker=CLP_Filters&fm=organic&iid=ae74e364-0bed-4954-9a9f-aadb1915d37b.MOBGHW44ZSN5EPGU.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', 'google pixel 7 (lemongrass, 128 gb)', '30999.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/l/2/y/-original-imaggswcffkgcupp.jpeg?q=70', '2025-12-16 20:43:28'),
(2, 1, 'https://www.flipkart.com/google-pixel-10-pro-xl-jade-256-gb/p/itm702fa25db1f13?pid=MOBHEXHRPRFQZE8H&lid=LSTMOBHEXHRPRFQZE8HBPV23X&marketplace=FLIPKART&store=tyy%2F4io&srno=b_2_37&otracker=CLP_Filters&fm=organic&iid=en_0FW4mGMItYmDEUsQsi0n9RT_r_VBoWGUd6JmCPkhwLlhkSShVPVFX4-AstoUbGshjBCgx2o-ncYrelKw5DjYzPUFjCTyOHoHZs-Z5_PS_w0%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', 'google pixel 10 pro xl (jade, 256 gb)', '124999.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/i/g/5/-original-imahfjsfkhqec3bu.jpeg?q=70', '2025-12-16 20:43:57'),
(3, 1, 'https://www.flipkart.com/google-pixel-10-pro-xl-jade-256-gb/p/itm702fa25db1f13?pid=MOBHEXHRPRFQZE8H&lid=LSTMOBHEXHRPRFQZE8HBPV23X&marketplace=FLIPKART&store=tyy%2F4io&srno=b_1_17&otracker=CLP_Filters&fm=organic&iid=en_vJOdJfY9G2n9Inre9WnUksU3FQK0ApxmXDVJaXevIdMxKwTJSMgZUlpUgYs6xnqp6FLwgjf1a1cvxqOcvULRTevN4Mn-dv-pi277bRzMbnY%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', 'google pixel 10 pro xl (jade, 256 gb)', '124999.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/i/g/5/-original-imahfjsfkhqec3bu.jpeg?q=70', '2025-12-16 20:44:28'),
(4, 1, 'https://www.flipkart.com/google-pixel-10-pro-jade-256-gb/p/itm56ea5d61cab29?pid=MOBHEXHRYASTHFKT&lid=LSTMOBHEXHRYASTHFKTIOACBA&marketplace=FLIPKART&store=tyy%2F4io&srno=b_1_11&otracker=CLP_Filters&fm=organic&iid=en_vJOdJfY9G2n9Inre9WnUksU3FQK0ApxmXDVJaXevIdOLttBrOV77z93LY9_--pZi7p-4NYMGbiFZQMfqlwznD4QEIsITtCzc4bHaOMTqL08%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', 'google pixel 10 pro (jade, 256 gb)', '109999.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/7/i/s/-original-imahfjsf5fxqvmhf.jpeg?q=70', '2025-12-16 20:45:08'),
(5, 1, 'https://www.flipkart.com/google-pixel-10-lemongrass-256-gb/p/itmb9d9694811d2e?pid=MOBHEXHRGZ3WMHNS&lid=LSTMOBHEXHRGZ3WMHNSYMLO3G&marketplace=FLIPKART&store=tyy%2F4io&srno=b_7_150&otracker=CLP_Filters&fm=organic&iid=b17b03dd-1866-49a0-a5ab-cdc27ad49aae.MOBHEXHRGZ3WMHNS.SEARCH&ppt=browse&ppn=browse&ssid=nv337feq800000001764861750489', 'google pixel 10 (lemongrass, 256 gb)', '79999.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/i/8/y/-original-imahfjsfdmpbbhhb.jpeg?q=70', '2025-12-16 21:09:48'),
(6, 1, 'https://www.flipkart.com/google-pixel-10-pro-porcelain-256-gb/p/itmb41080c79ef00?pid=MOBHEXHRMGFJ93DM&lid=LSTMOBHEXHRMGFJ93DMPLAAAK&marketplace=FLIPKART&store=tyy%2F4io&srno=b_23_530&otracker=CLP_Filters&fm=organic&iid=45d6fb3b-3479-471b-85b3-01ff75e93ff5.MOBHEXHRMGFJ93DM.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', 'google pixel 10 pro (porcelain, 256 gb)', '109999.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/e/q/d/-original-imahfjsfyhzntaux.jpeg?q=70', '2025-12-16 21:19:51'),
(7, 2, 'https://www.amazon.in/Allen-Solly-Geometric-Regular-ASSFWMOFI31587_White_42/dp/B07DMVHSQ1/ref=sr_1_40?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.bYIURbUF8gj_S5PXtkQXGYM7ptVlq4lp8ZLgZ4ovAQ_2Ign4VGh5OQ2E4OuLGswFxiDVgSuF6mdajYGkGCRP13k20i0Ygl5wmroB0eYmdpCJ2n5Dg3MkjWtDbWvDLtw8k5vTnp-X5Phdzm12t2O2R6cftyGn_FallehHrwOSMMios0KQ-Jmy6STPZ_N6E2v9XK9gyjRzxJTQ1Q80rGToh_chLmBq6nCMSnwmeVy89ks6mntxDa3O2w2C-R019rjpQSmDWQhwsPEstoZmVi6u_7FGvvTdxs0__rRN--5MuDg.Bt_w-ob_fdo94Gv4bWPiomI5GULI1VkAlmvNU0xg99I&dib_tag=se&keywords=men+fashion+clothes&qid=1764906841&sprefix=men+fashion%2Caps%2C271&sr=8-40', 'men shirt', '749.00', 'https://m.media-amazon.com/images/I/51hflOoXp7L._AC_UL320_.jpg', '2025-12-19 11:21:30'),
(8, 2, 'https://www.amazon.in/Lymio-Regular-Shirt-Stylish-Resort-Slub/dp/B0DZCVHK27/ref=sr_1_35?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.bYIURbUF8gj_S5PXtkQXGYM7ptVlq4lp8ZLgZ4ovAQ_2Ign4VGh5OQ2E4OuLGswFxiDVgSuF6mdajYGkGCRP13k20i0Ygl5wmroB0eYmdpCJ2n5Dg3MkjWtDbWvDLtw8k5vTnp-X5Phdzm12t2O2R6cftyGn_FallehHrwOSMMios0KQ-Jmy6STPZ_N6E2v9XK9gyjRzxJTQ1Q80rGToh_chLmBq6nCMSnwmeVy89ks6mntxDa3O2w2C-R019rjpQSmDWQhwsPEstoZmVi6u_7FGvvTdxs0__rRN--5MuDg.Bt_w-ob_fdo94Gv4bWPiomI5GULI1VkAlmvNU0xg99I&dib_tag=se&keywords=men+fashion+clothes&qid=1764906841&sprefix=men+fashion%2Caps%2C271&sr=8-35', 'men cotton regular fit shirt || stylish (resort-slub)', '419.00', 'https://m.media-amazon.com/images/I/71pwj3RiXsL._AC_UL320_.jpg', '2025-12-19 11:21:34'),
(9, 3, 'https://www.flipkart.com/google-pixel-7-lemongrass-128-gb/p/itm45d75002be0e7?pid=MOBGHW44ZSN5EPGU&lid=LSTMOBGHW44ZSN5EPGUVDQE3A&marketplace=FLIPKART&store=tyy%2F4io&srno=b_40_945&otracker=CLP_Filters&fm=organic&iid=ae74e364-0bed-4954-9a9f-aadb1915d37b.MOBGHW44ZSN5EPGU.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', 'google pixel 7 (lemongrass, 128 gb)', '30999.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/l/2/y/-original-imaggswcffkgcupp.jpeg?q=70', '2025-12-20 20:48:04'),
(10, 3, 'https://www.flipkart.com/google-pixel-10-pro-jade-256-gb/p/itm56ea5d61cab29?pid=MOBHEXHRYASTHFKT&lid=LSTMOBHEXHRYASTHFKTIOACBA&marketplace=FLIPKART&store=tyy%2F4io&srno=b_2_32&otracker=CLP_Filters&fm=organic&iid=en_0FW4mGMItYmDEUsQsi0n9RT_r_VBoWGUd6JmCPkhwLmNEOj6Z5krJUBKXj4dW-CmOzOIsqGbAMLFtiDJD5SLRg%3D%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', 'google pixel 10 pro (jade, 256 gb)', '109999.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/7/i/s/-original-imahfjsf5fxqvmhf.jpeg?q=70', '2025-12-20 20:49:02'),
(11, 3, 'https://www.flipkart.com/google-pixel-10-pro-jade-256-gb/p/itm56ea5d61cab29?pid=MOBHEXHRYASTHFKT&lid=LSTMOBHEXHRYASTHFKTIOACBA&marketplace=FLIPKART&store=tyy%2F4io&srno=b_1_11&otracker=CLP_Filters&fm=organic&iid=en_vJOdJfY9G2n9Inre9WnUksU3FQK0ApxmXDVJaXevIdOLttBrOV77z93LY9_--pZi7p-4NYMGbiFZQMfqlwznD4QEIsITtCzc4bHaOMTqL08%3D&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', 'google pixel 10 pro (jade, 256 gb)', '109999.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/7/i/s/-original-imahfjsf5fxqvmhf.jpeg?q=70', '2025-12-20 20:49:46'),
(12, 3, 'https://www.flipkart.com/google-pixel-7a-coral-128-gb/p/itmb4d7b100b1a4d?pid=MOBGT5F26QJYZUZS&lid=LSTMOBGT5F26QJYZUZSUUTWOI&marketplace=FLIPKART&store=tyy%2F4io&srno=b_26_616&otracker=CLP_Filters&fm=organic&iid=2400bfa7-6aab-4554-8dac-26e0c81d4eca.MOBGT5F26QJYZUZS.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', 'google pixel 7a (coral, 128 gb)', '28999.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/i/a/r/-original-imagtrf9qm3dufq9.jpeg?q=70', '2025-12-24 09:03:11'),
(13, 3, 'https://www.amazon.in/AWG-ALL-WEATHER-GEAR-Windcheater/dp/B0FTVHXSRX/ref=sr_1_219?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.Fm0MWebXZADrW6_KFAV4Czl2mW4troaQrCEIiMN6ncq_CeFTVzuV7390DvqGR1D1627vqdpqKsgyH3MLHTYz_ew-PZd2PxR-i5NIK5Q9kkleZ_xQLqgxJIgBC9J--Cy2gdRS8ICKydRn5sM6aoGW0L01eXG-yLhjM9sVC6wJK-X_FrzxyRsFKTWBUbzepabPJfi1NOEDgPRL8OKm9E0PoLN-Vpp8x0eW7FFaT27Qh2maWNEkQYxqAspCDvwDkrK1h7XbFh02lwZDmH9qu6hckgJqcQEgUpDMOa-LetDvpfY.FABnphS1CupA8-HFbqZHO-ChaDV9QOSzz-a96U7giNU&dib_tag=se&keywords=men+fashion+clothes&qid=1764907092&sprefix=men+fashion%2Caps%2C271&sr=8-219&xpid=-m7_BlYD0bePS', 'jacket for men', '929.00', 'https://m.media-amazon.com/images/I/61nA7Yhg67L._AC_UL320_.jpg', '2025-12-24 10:27:16'),
(14, 3, 'https://www.amazon.in/Lymio-Jackets-Lightweight-Outwear-J-9-Grey-XL/dp/B0FK9JPFYP/ref=sr_1_10?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.bYIURbUF8gj_S5PXtkQXGYM7ptVlq4lp8ZLgZ4ovAQ_2Ign4VGh5OQ2E4OuLGswFxiDVgSuF6mdajYGkGCRP13k20i0Ygl5wmroB0eYmdpCJ2n5Dg3MkjWtDbWvDLtw8k5vTnp-X5Phdzm12t2O2R6cftyGn_FallehHrwOSMMios0KQ-Jmy6STPZ_N6E2v9XK9gyjRzxJTQ1Q80rGToh_chLmBq6nCMSnwmeVy89ks6mntxDa3O2w2C-R019rjpQSmDWQhwsPEstoZmVi6u_7FGvvTdxs0__rRN--5MuDg.Bt_w-ob_fdo94Gv4bWPiomI5GULI1VkAlmvNU0xg99I&dib_tag=se&keywords=men+fashion+clothes&qid=1764906841&sprefix=men+fashion%2Caps%2C271&sr=8-10', 'jackets || jacket for men || lightweight outwear jacket (j-07-09)', '703.00', 'https://m.media-amazon.com/images/I/61YT6E6bWvL._AC_UL320_.jpg', '2025-12-24 10:27:22'),
(15, 1, 'https://www.amazon.in/sspa/click?ie=UTF8&spc=MToyMTMwNTQ3MDg0MzU0NjM4OjE3NjQ5MDY5MjE6c3BfYXRmX25leHQ6MzAwNzg0NjM2NTUzNTMyOjowOjo&url=%2FBoldfit-Polyester-Sweatshirt-Bftbm4022S-Bkxxl_Black%2Fdp%2FB0DKNXF3N3%2Fref%3Dsr_1_97_sspa%3Fcrid%3D28H7076H9RSND%26dib%3DeyJ2IjoiMSJ9.AH0p9K-bR6tBnJMQ_twf7QAMr2MHsmEQHwLBr6sIJEzGv4VJ3fP5aUmNeGTmavUOX2dAdd35a6zX5t5eoeGP5lUJuBb6hBSnUNj5jFAyI3c.uOlRsvy2jClD__V8kGbdqvrX4-EPbdMlMWoNx6pbTz4%26dib_tag%3Dse%26keywords%3Dmen%2Bfashion%2Bclothes%26qid%3D1764906920%26sprefix%3Dmen%2Bfashion%252Caps%252C271%26sr%3D8-97-spons%26xpid%3D-m7_BlYD0bePS%26aref%3DPWUUyMKpDu%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGZfbmV4dA%26psc%3D1&aref=PWUUyMKpDu&sp_cr=ZAZ', 'men full zip', '799.00', 'https://m.media-amazon.com/images/I/61W-qDio3BL._AC_UL320_.jpg', '2025-12-27 09:00:36'),
(16, 1, 'https://www.amazon.in/Allen-Solly-Geometric-Regular-ASSFWMOFI31587_White_42/dp/B07DMVHSQ1/ref=sr_1_40?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.bYIURbUF8gj_S5PXtkQXGYM7ptVlq4lp8ZLgZ4ovAQ_2Ign4VGh5OQ2E4OuLGswFxiDVgSuF6mdajYGkGCRP13k20i0Ygl5wmroB0eYmdpCJ2n5Dg3MkjWtDbWvDLtw8k5vTnp-X5Phdzm12t2O2R6cftyGn_FallehHrwOSMMios0KQ-Jmy6STPZ_N6E2v9XK9gyjRzxJTQ1Q80rGToh_chLmBq6nCMSnwmeVy89ks6mntxDa3O2w2C-R019rjpQSmDWQhwsPEstoZmVi6u_7FGvvTdxs0__rRN--5MuDg.Bt_w-ob_fdo94Gv4bWPiomI5GULI1VkAlmvNU0xg99I&dib_tag=se&keywords=men+fashion+clothes&qid=1764906841&sprefix=men+fashion%2Caps%2C271&sr=8-40', 'men shirt', '749.00', 'https://m.media-amazon.com/images/I/51hflOoXp7L._AC_UL320_.jpg', '2025-12-27 09:02:57'),
(17, 1, 'https://www.amazon.in/Puma-Dazzler-Peacoat-High-Red-PUMA-Sneaker/dp/B09XXL9D7K/ref=sr_1_27?crid=3RHED1UY34ZEC&dib=eyJ2IjoiMSJ9.yJWiNZUqAyKcgoyahgIhhE7gtA0BNJQfjFHBOlZEn6qmZsBwomYibmWAg7_L6UJiW-RdbF1TKJiU2wscrSMTyoDP3e376uJlzoh1l27kGbGZYhdAWFqgJycAvG20Bwlq5SwGueaWMLSu9xhhWiwGEVJPmStNqGoL4qC7_b-7_F72uaLjhhbGsnppForErfIrTWkQ4twYQcfXK9I4bzqeGxzuaOiUWm39lSzWP_y3jV1u6_kcfLRCYQylsuS39MSaUmXP66xUMVXC0KxeYj7WyKZHwXSarWb5Sm7I-O2JQtk.Pvdo0mMbqM66LJgK19V-Ntvz4hxyevvzdZkrtNIhgvI&dib_tag=se&keywords=shoes&qid=1764679369&sprefix=shoes%2Caps%2C465&sr=8-27', 'mens dazzler sneaker', '1099.00', 'https://m.media-amazon.com/images/I/61C-Z8IFLBL._AC_UL320_.jpg', '2025-12-27 10:03:38'),
(18, 1, 'https://www.amazon.in/BULLMER-Clothing-Trendy-Shirt-Co-ords/dp/B0D1CG56ND/ref=sr_1_141?crid=28H7076H9RSND&dib=eyJ2IjoiMSJ9.XK9vFrN9WsmzvPCbS25EM686rz7AKaOEgR8HjGyvl73ukrun7nkdjSbmWXUHSinOKfFrMucPJ-z83Ku5TuPe1JiMF_MZoK6sbkYG60UWZnUzRuRcp0hLDC9CPU8MsgpopxaU9opdliEPp1nmHmNdFkP-7L0OHnybTckE9UL4YNbHlBQzx_m290qcvlfXCdxUy1sBNJx3CSHpngeZpr8fXDctgapPwe7TWGj4UEb0P9j3f8HTr_a3PfUDx6zQDs-9jgsiUDDqIyNQSG-zIg-wH1cHrwygiZjp9LU6cFLyW1U.YxJ2MY84EMKHUQGsrwe2nGxAgYbe2iIbW7IaXi_pN2c&dib_tag=se&keywords=men+fashion+clothes&qid=1764906920&sprefix=men+fashion%2Caps%2C271&sr=8-141&xpid=-m7_BlYD0bePS', 'clothing set with trendy shirt & pants co-ords for men', '778.00', 'https://m.media-amazon.com/images/I/51zH4SGb6hL._AC_UL320_.jpg', '2025-12-27 10:18:00'),
(19, 1, 'https://www.flipkart.com/vivo-y18t-gem-green-128-gb/p/itme070e0d6f5af3?pid=MOBH5VZZYVAK5DEK&lid=LSTMOBH5VZZYVAK5DEKP89HYU&marketplace=FLIPKART&store=tyy%2F4io&srno=b_30_697&otracker=CLP_Filters&fm=organic&iid=530060d2-858c-498c-b482-6fbf9ded2032.MOBH5VZZYVAK5DEK.SEARCH&ppt=browse&ppn=browse&ssid=g2lo4ufgg00000001764683789782', 'vivo y18t (gem green, 128 gb)', '8499.00', 'https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/i/l/0/-original-imah6ag3vqmhas4m.jpeg?q=70', '2025-12-27 11:23:24');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alerts`
--
ALTER TABLE `alerts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `price_history`
--
ALTER TABLE `price_history`
  ADD PRIMARY KEY (`history_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD PRIMARY KEY (`wishlist_id`),
  ADD UNIQUE KEY `unique_product_user` (`user_id`,`product_hash`) USING HASH,
  ADD KEY `idx_product_hash` (`product_hash`(768));

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `alerts`
--
ALTER TABLE `alerts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `price_history`
--
ALTER TABLE `price_history`
  MODIFY `history_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `wishlist`
--
ALTER TABLE `wishlist`
  MODIFY `wishlist_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
