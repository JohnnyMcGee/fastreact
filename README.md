# fastreact

fastreact (**Re**Charge **A**PI **C**lient **T**ool) is a ReCharge Payments API client wrapper. 
You can query customers, orders and subscriptions.



`python3 fastreact.py -o 5555555555`


```
Set input order to [ 5555555555 ]
Searching ReCharge orders.....
Searching Shopify orders....
{
   "next_cursor": null,
   "previous_cursor": null,
   "orders": [
      {
         "id": 1231231123,
         "address_id": 123123123,
         "billing_address": {
            ...
```





# Requirements
- python3
- smile on your face

# Usage

```
pip install -r requirements.txt
```

# Config
edit `config.json` with your API token

`indent_level` is the amount of tabs for  the JSON formatted data

`data_sort` is to sort  JSON formatted data (a-z)


(if you wanna make things official)

`ln -s ./fastreact.py /usr/local/bin/fastreact`

## Search customers by email
```
./fastreact -c larry@google.com
```
## Search customers by customer ID (Shopify or ReCharge customer IDs)
```
./fastreact -c 420000069
```

## Search by order ID with colour
```
./fastreact -o 48282910 -z
```

## Search by subscription ID
```
./fastreact -s 3242342
```