How to run tests
================
We implement our test using Python unittests.
Currently, we do not have automatic testing in our CI.
This is still work in progress.
However, we do testing locally.
Easiest way to run out implemented tests to follow this instructions

1. clone the repo
2. prepare and `.env.filip` file with the following content:

```
CB_URL="http://yourContextBrokerHost:Port"
IOTA_URL="http://yourIoTAgentHost:Port"
QL_URL="http://yourQuantumleapHost:Port"
```  

3. Put the file next to the testing scenarios
4. Run the files in the development environment of your choice

