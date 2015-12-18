-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u1build0.15.04.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Dic 18, 2015 alle 14:08
-- Versione del server: 5.6.27-0ubuntu0.15.04.1
-- PHP Version: 5.6.4-4ubuntu6.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `orchestrator`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `domains_gre`
--

CREATE TABLE IF NOT EXISTS `domains_gre` (
  `id` int(64) NOT NULL,
  `name` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `domains_info_id` int(64) NOT NULL,
  `local_ip` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `remote_ip` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `gre_key` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dump dei dati per la tabella `domains_gre`
--

INSERT INTO `domains_gre` (`id`, `name`, `domains_info_id`, `local_ip`, `remote_ip`, `gre_key`) VALUES
(0, 'gre1', 0, '1.1.1.1', NULL, '156'),
(1, 'gre1', 3, '2.2.2.2', NULL, '123'),
(2, 'gre1', 5, '20.20.21.12', NULL, '123');

-- --------------------------------------------------------

--
-- Struttura della tabella `domains_information`
--

CREATE TABLE IF NOT EXISTS `domains_information` (
  `id` int(64) NOT NULL,
  `domain_ip` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `domain_name` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `interface` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `interface_type` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `neighbor` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `gre` tinyint(1) NOT NULL,
  `vlan` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dump dei dati per la tabella `domains_information`
--

INSERT INTO `domains_information` (`id`, `domain_ip`, `domain_name`, `interface`, `interface_type`, `neighbor`, `gre`, `vlan`) VALUES
(0, '10.0.0.1', 'domain0', 'eth1', 'ethernetCsmacd', 'domain1/eth2', 1, 1),
(1, '10.0.0.1', 'domain0', 'eth2', 'ppoe', 'domain2/eth3', 0, 0),
(2, '10.0.0.1', 'domain0', 'eth3', 'ppoe', 'domain2/eth21', 0, 0),
(3, '10.0.0.2', 'domain1', 'eth2', 'ethernetCsmacd', 'domain0/eth1', 1, 1),
(4, '10.0.0.2', 'domain1', 'eth20', 'ethernetCsmacd', NULL, 0, 0),
(5, '10.0.0.3', 'domain2', 'eth3', 'ethernetCsmacd', 'domain0/eth2', 1, 1),
(6, '10.0.0.3', 'domain2', 'eth21', 'ethernetCsmacd', 'domain0/eth3', 0, 0);

-- --------------------------------------------------------

--
-- Struttura della tabella `domains_vlan`
--

CREATE TABLE IF NOT EXISTS `domains_vlan` (
  `id` int(64) NOT NULL,
  `domains_info_id` int(64) NOT NULL,
  `vlan` varchar(64) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `graph`
--

CREATE TABLE IF NOT EXISTS `graph` (
  `id` int(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `node_id` varchar(64) DEFAULT NULL,
  `partial` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `node`
--

CREATE TABLE IF NOT EXISTS `node` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `type` varchar(64) NOT NULL,
  `domain_id` varchar(64) NOT NULL,
  `ca_ip` varchar(64) NOT NULL,
  `ca_port` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dump dei dati per la tabella `node`
--

INSERT INTO `node` (`id`, `name`, `type`, `domain_id`, `ca_ip`, `ca_port`) VALUES
('0', 'node0', 'OpenStack+CA', '130.192.225.105', '', 0),
('1', 'nodo-to:sw1', 'JolnetCA', 'openflow:110953238266560', '', 0),
('10', 'nodo-to:sw1', 'JolnetCA', '00:00:64:e9:50:5a:82:c0', '', 0),
('101', 'node1', 'OpenStack+_compute', '130.192.225.193', '', 0),
('11', 'cpe-to:sw1', 'JolnetCA', 'openflow:110953238270016', '', 0),
('12', 'cpe-to:sw1', 'JolnetCA', '00:00:64:e9:50:5a:90:40', '', 0),
('2', 'nodo-mi:sw1', 'JolnetCA', 'openflow:110953238267840', '', 0),
('20', 'nodo-mi:sw1', 'JolnetCA', '00:00:64:e9:50:5a:87:c0', '', 0),
('200', 'node2', 'OpenStack+_compute', '10.0.0.3', '10.0.0.3', 8000),
('21', 'cpe-mi:sw1', 'JolnetCA', 'openflow:110953238267072', '', 0),
('22', 'cpe-mi:sw1', 'JolnetCA', '00:00:64:e9:50:5a:84:c0', '', 0),
('244', 'Jolnet_controller', 'JolnetCA', '163.162.234.44', '', 0),
('3', 'nodo-ti:sw1', 'JolnetCA', 'openflow:110953238268480', '', 0),
('30', 'nodo-ti:sw1', 'JolnetCA', '00:00:64:e9:50:5a:8a:40', '', 0),
('300', 'node3', 'UniversalNodeCA', '10.0.0.1', '10.0.0.1', 9000),
('31', 'cpe-ti:sw1', 'JolnetCA', 'openflow:110953238265624', '', 0),
('32', 'cpe-ti:sw1', 'JolnetCA', '00:00:64:e9:50:5a:7f:18', '', 0),
('4', 'nodo-tn:sw1', 'JolnetCA', 'openflow:44838630154304', '', 0),
('40', 'nodo-tn:sw1', 'JolnetCA', '00:00:28:c7:ce:9f:60:40', '', 0),
('400', 'node4', 'UnifiedNode', '10.0.0.5', '', 0),
('41', 'cpe-tn:sw1', 'JolnetCA', 'openflow:968199681216', '', 0),
('42', 'cpe-tn:sw1', 'JolnetCA', '00:00:00:e1:6d:32:b4:c0', '', 0),
('490', 'node45', 'UniversalNodeCA', '10.0.0.2', '10.0.0.2', 7500),
('5', 'nodo-pi:sw1', 'JolnetCA', 'openflow:58119451054400', '', 0),
('50', 'nodo-pi:sw1', 'JolnetCA', '00:00:34:db:fd:3c:11:40', '', 0),
('51', 'cpe-pi:sw1', 'JolnetCA', 'openflow:110953239436736', '', 0),
('52', 'cpe-pi:sw1', 'JolnetCA', '00:00:64:e9:50:6c:5d:c0', '', 0),
('567', 'Heat_node', 'HeatCA', '130.192.225.193', '', 0),
('6', 'nodo-ct:sw1', 'JolnetCA', 'openflow:110953238258240', '', 0),
('60', 'nodo-ct:sw1', 'JolnetCA', '00:00:64:e9:50:5a:62:40', '', 0),
('61', 'cpe-ct:sw1', 'JolnetCA', 'openflow:110953239438656', '', 0),
('62', 'cpe-ct:sw1', 'JolnetCA', '00:00:64:e9:50:6c:65:40', '', 0),
('6456', 'Heat_ctrl', 'HeatCA', 'controller.ipv6.polito.it', '', 0);

-- --------------------------------------------------------

--
-- Struttura della tabella `session`
--

CREATE TABLE IF NOT EXISTS `session` (
  `id` varchar(64) NOT NULL,
  `user_id` varchar(64) DEFAULT NULL,
  `service_graph_id` varchar(64) NOT NULL,
  `service_graph_name` varchar(64) NOT NULL,
  `ingress_node` varchar(64) DEFAULT NULL,
  `egress_node` varchar(64) DEFAULT NULL,
  `status` varchar(64) NOT NULL,
  `started_at` datetime DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  `error` datetime DEFAULT NULL,
  `ended` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dump dei dati per la tabella `session`
--

INSERT INTO `session` (`id`, `user_id`, `service_graph_id`, `service_graph_name`, `ingress_node`, `egress_node`, `status`, `started_at`, `last_update`, `error`, `ended`) VALUES
('b49ff9c556f947f38e4c8e6126891a9b', '1', '3_base', 'Forwarding graph', '300', '200', 'complete', '2015-12-17 15:20:08', '2015-12-17 15:20:08', NULL, '2015-12-17 15:22:31');

-- --------------------------------------------------------

--
-- Struttura della tabella `tenant`
--

CREATE TABLE IF NOT EXISTS `tenant` (
  `id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `name` varchar(64) CHARACTER SET utf8 NOT NULL,
  `description` varchar(128) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dump dei dati per la tabella `tenant`
--

INSERT INTO `tenant` (`id`, `name`, `description`) VALUES
('0', 'demo', 'Demo tenant'),
('1', 'PoliTO_chain1', 'Tenant to access the Jolnet'),
('2', 'demo2', 'Demo2 Tenant');

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

--
-- Dump dei dati per la tabella `user`
--

INSERT INTO `user` (`id`, `name`, `password`, `tenant_id`, `mail`) VALUES
('0', 'demo', 'stack', '0', NULL),
('1', 'AdminPoliTO', 'AdminPoliTO', '1', NULL),
('2', 'demo2', 'stack', '2', NULL);

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
-- Indexes for dumped tables
--

--
-- Indexes for table `domains_gre`
--
ALTER TABLE `domains_gre`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `domains_information`
--
ALTER TABLE `domains_information`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `domains_vlan`
--
ALTER TABLE `domains_vlan`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `graph`
--
ALTER TABLE `graph`
 ADD PRIMARY KEY (`id`), ADD UNIQUE KEY `service_graph_id` (`session_id`,`node_id`);

--
-- Indexes for table `node`
--
ALTER TABLE `node`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `session`
--
ALTER TABLE `session`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tenant`
--
ALTER TABLE `tenant`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `vnf_image`
--
ALTER TABLE `vnf_image`
 ADD PRIMARY KEY (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
