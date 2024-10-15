#!/usr/bin/env bash

PHP_VERSION=7.4
IONCUBE_VERSION=12.0.2
TESTRAIL_DB_NAME=testrail
TESTRAIL_DB_USER=testrail
TESTRAIL_DB_PASSWORD=testrail

DEBIAN_FRONTEND=noninteractive
echo "Updating Software"
sudo apt-get update
sudo apt-get install -y unzip
sudo apt install software-properties-common
sudo add-apt-repository ppa:ondrej/php -y

#Install Apache web server
echo "Install Apache Server"
sudo apt-get install -y apache2 

#Install PHP and extensions 
echo "Install PHP Extensions"
sudo apt-get install -y php${PHP_VERSION} php${PHP_VERSION}-{mysql,curl,json,mbstring,xml,zip,gd,ldap}

#download ioncube loader
echo "Install ioncube loader extension"
wget  -O /tmp/ioncube.tar.gz http://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64_${IONCUBE_VERSION}.tar.gz
sudo tar -xzf /tmp/ioncube.tar.gz -C /tmp
sudo mv /tmp/ioncube /opt/ioncube
rm -f /tmp/ioncube.tar.gz
sudo mkdir -p /usr/local/etc/php/
echo zend_extension=/opt/ioncube/ioncube_loader_lin_${PHP_VERSION}.so | sudo tee /etc/php/7.4/apache2/conf.d/00-ioncube.ini > /dev/null
echo zend_extension=/opt/ioncube/ioncube_loader_lin_${PHP_VERSION}.so | sudo tee /etc/php/7.4/cli/conf.d/00-ioncube.ini > /dev/null

sudo service apache2 restart

#install MariaDB
echo "Install MariaDB"
sudo sudo apt-get install -y mariadb-server mariadb-client
echo "CREATE DATABASE ${TESTRAIL_DB_NAME} DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;" | sudo mysql -uroot
echo "CREATE USER '${TESTRAIL_DB_USER}'@'localhost' IDENTIFIED BY '${TESTRAIL_DB_PASSWORD}';" | sudo mysql -uroot
echo "GRANT ALL ON ${TESTRAIL_DB_NAME}.* TO '${TESTRAIL_DB_USER}'@'localhost';" | sudo mysql -uroot

#install cassandra
echo "Install Java"
sudo sudo apt-get install -y openjdk-8-jdk 

echo "multiarch-support_2"
cd /tmp
wget http://archive.ubuntu.com/ubuntu/pool/main/g/glibc/multiarch-support_2.27-3ubuntu1.6_amd64.deb
sudo dpkg -i multiarch-support_2.27-3ubuntu1.6_amd64.deb
echo "Cassandra cpp driver"
wget https://downloads.datastax.com/cpp-driver/ubuntu/18.04/cassandra/v2.16.0/cassandra-cpp-driver_2.16.0-1_amd64.deb
sudo dpkg -i cassandra-cpp-driver_2.16.0-1_amd64.deb

echo "Install Cassandra PHP Drivers"
sudo sudo apt-get install -y git
git clone https://git.assembla.com/gurock/Drivers.Cassandra.git cassandra_drivers

PHP_EXT_DIR=$(php -i | grep -o -P '(?<=extension_dir => ).*\w+(?=\s)')
cd /tmp
sudo cp cassandra_drivers/Linux/${PHP_VERSION}/cassandra.so ${PHP_EXT_DIR}
echo extension=cassandra.so | sudo tee /etc/php/${PHP_VERSION}/apache2/conf.d/01-cassandra.ini > /dev/null
echo extension=cassandra.so | sudo tee /etc/php/${PHP_VERSION}/cli/conf.d/01-cassandra.ini > /dev/null
sudo service apache2 restart

echo "Install Cassandra"
sudo apt-get install -y apt-transport-https gnupg2 
wget -q -O - https://www.apache.org/dist/cassandra/KEYS | sudo apt-key add -
sh -c 'echo "deb http://www.apache.org/dist/cassandra/debian 311x main" > /etc/apt/sources.list.d/cassandra.list'
sudo apt-get update -y
sudo apt-get install python2
sudo apt-get install cassandra -y
sudo wget -O /usr/share/cassandra/lib/cassandra-lucene-index-plugin-3.11.3.0.jar https://repo1.maven.org/maven2/com/stratio/cassandra/cassandra-lucene-index-plugin/3.11.3.0/cassandra-lucene-index-plugin-3.11.3.0.jar
sudo service cassandra restart
sleep 5
echo "CREATE KEYSPACE IF NOT EXISTS testrail WITH REPLICATION={'class': 'SimpleStrategy', 'replication_factor': 1};" | cqlsh

echo "Install Testrail"
cd /tmp
wget https://secure.gurock.com/downloads/testrail/testrail-7.5.3.1000-ion72.zip
sudo unzip -q testrail-7.5.3.1000-ion72.zip -d /var/www/html
sudo mkdir /var/www/html/testrail/logs/
sudo mkdir /var/www/html/testrail/audit/
sudo mkdir -p /opt/testrail/attachments/
sudo mkdir -p /opt/testrail/reports/
sudo chown -R www-data:www-data /var/www/html/testrail
sudo chown -R www-data:www-data /opt/testrail

echo "* * * * * www-data /usr/bin/php /var/www/html/testrail/task.php" | sudo tee /etc/cron.d/testrail > /dev/null
echo "Testrail installed successfully"