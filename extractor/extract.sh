#!/bin/bash
 
# Declare an array of string
declare -a SpiderArray=("boiteagraines kokopelli biaugerme fermedesaintmarthe comptoirdesgraines sanrival grainesdelpais")
 
# Iterate the string array using for loop
for spider in ${SpiderArray[@]}; do
   scrapy crawl $spider -O data/$spider.json
done