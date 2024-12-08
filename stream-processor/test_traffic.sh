#!/bin/bash
# Simulate traffic to product pages

for i in {1..100}; do
    # 50% - product1
    curl http://localhost:8080/product1.html
    curl http://localhost:8080/product1.html
    
    # 25% - product2
    curl http://localhost:8080/product2.html
    
    # 15% - product3
    if [ $((RANDOM % 100)) -lt 15 ]; then
        curl http://localhost:8080/product3.html
    fi
    
    # 8% - product4
    if [ $((RANDOM % 100)) -lt 8 ]; then
        curl http://localhost:8080/product4.html
    fi
    
    # 2% - product5
    if [ $((RANDOM % 100)) -lt 2 ]; then
        curl http://localhost:8080/product5.html
    fi
    
    sleep 0.1
done
