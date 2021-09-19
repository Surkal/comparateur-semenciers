#!/bin/bash
 
# Declare an array of spider names
declare -a SpiderArray=("boiteagraines kokopelli biaugerme fermedesaintmarthe comptoirdesgraines sanrival grainesdelpais grainesbaumaux potageetgourmands")

 
# Iterate the string array using for loop
for spider in ${SpiderArray[@]}; do
   scrapy crawl $spider -O data/$spider.json --logfile logs/$spider.log &
done