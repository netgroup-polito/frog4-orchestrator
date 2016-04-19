-- phpMyAdmin SQL Dump
-- version 4.4.13.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Creato il: Apr 19, 2016 alle 14:03
-- Versione del server: 5.6.28-0ubuntu0.15.10.1
-- Versione PHP: 5.6.11-1ubuntu3.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `orchestrator`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `domain`
--

CREATE TABLE IF NOT EXISTS `domain` (
  `id` int(11) NOT NULL,
  `name` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `type` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `ip` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `port` int(11) NOT NULL,
  `token` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `domain_gre`
--

CREATE TABLE IF NOT EXISTS `domain_gre` (
  `id` int(64) NOT NULL,
  `name` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `domain_info_id` int(64) NOT NULL,
  `local_ip` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `remote_ip` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `gre_key` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `domain_information`
--

CREATE TABLE IF NOT EXISTS `domain_information` (
  `id` int(64) NOT NULL,
  `domain_id` int(11) NOT NULL,
  `node` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `interface` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `interface_type` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `gre` tinyint(1) NOT NULL,
  `vlan` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `domain_neighbor`
--

CREATE TABLE IF NOT EXISTS `domain_neighbor` (
  `id` int(11) NOT NULL,
  `domain_info_id` int(11) NOT NULL,
  `neighbor_domain_name` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `neighbor_node` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `neighbor_interface` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `neighbor_domain_type` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `domain_vlan`
--

CREATE TABLE IF NOT EXISTS `domain_vlan` (
  `id` int(64) NOT NULL,
  `domain_info_id` int(64) NOT NULL,
  `vlan_start` int(11) NOT NULL,
  `vlan_end` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `graph`
--

CREATE TABLE IF NOT EXISTS `graph` (
  `id` int(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `domain_id` int(11) DEFAULT NULL,
  `partial` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `session`
--

CREATE TABLE IF NOT EXISTS `session` (
  `id` varchar(64) NOT NULL,
  `user_id` varchar(64) DEFAULT NULL,
  `service_graph_id` varchar(64) NOT NULL,
  `service_graph_name` varchar(64) NOT NULL,
  `ingress_domain` varchar(64) DEFAULT NULL,
  `egress_domain` varchar(64) DEFAULT NULL,
  `status` varchar(64) NOT NULL,
  `started_at` datetime DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  `error` datetime DEFAULT NULL,
  `ended` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `tenant`
--

CREATE TABLE IF NOT EXISTS `tenant` (
  `id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `name` varchar(64) CHARACTER SET utf8 NOT NULL,
  `description` varchar(128) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `name` varchar(64) CHARACTER SET utf8 NOT NULL,
  `password` varchar(64) CHARACTER SET utf8 NOT NULL,
  `tenant_id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `mail` varchar(64) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `vnf_image`
--

CREATE TABLE IF NOT EXISTS `vnf_image` (
  `id` varchar(255) NOT NULL,
  `internal_id` varchar(255) NOT NULL,
  `template` text NOT NULL,
  `configuration_model` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `domain`
--
ALTER TABLE `domain`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `domain_gre`
--
ALTER TABLE `domain_gre`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `domain_information`
--
ALTER TABLE `domain_information`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `domain_neighbor`
--
ALTER TABLE `domain_neighbor`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `domain_vlan`
--
ALTER TABLE `domain_vlan`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `graph`
--
ALTER TABLE `graph`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `service_graph_id` (`session_id`,`domain_id`);

--
-- Indici per le tabelle `session`
--
ALTER TABLE `session`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `tenant`
--
ALTER TABLE `tenant`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `vnf_image`
--
ALTER TABLE `vnf_image`
  ADD PRIMARY KEY (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
