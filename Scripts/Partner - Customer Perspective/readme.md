# Customer Persective for Partners
## Partner-Customer Account Tagger.py
- This script makes use of CloudHealth Partner APIs to lookup accounts associated with each customer, and tag the accounts in the partner tenant with the name of the customer they are associated with.
- This script assumes a given account is only found in one customer. In the event an account is found in multiple customers, the account will be tagged with the name of the most recently created customer where this account was found, not where the account may have been assigned most recently, or any other logic.
- This script shoudl be run at some interval in order to ensure all accounts are properly tagged as they are added to customers.

## Partner-Customer Perspective.py
- This script will create a Perspective categorizing AWS accounts tagged with the key CHT_Customer. This script needs only to be run once to create the perspective. 
- This perspective is built in a way such that any new accounts or customers tagged by 'Partner-Customer Account Tagger.py' will be associated with the corresponding customer.