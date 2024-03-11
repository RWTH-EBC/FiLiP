# Exercise 8: MultiEntity and Expression Language

The MultiEntity plugin Allows the devices provisioned in the IoTAgent to map their attributes to more than one entity,
declaring the target entity through the Configuration or Device provisioning APIs.

The IoTAgent Library provides an expression language for measurement transformation, that can be used to adapt the
information coming from the South Bound APIs to the information reported to the Context Broker. This is really useful
when you need to adapt measure.

There are available two different expression languages jexl and legacy. The recommended language to use is jexl,
which is newer and most powerful.

We want to apply these features to `e8_multientity_and_expression_language.py`.

The input sections are marked with 'TODO'

#### Steps to complete:
1. Setting up the expression language jexl
2. Applying the expression language to device attributes
3. Testing the expression language via MQTT messages
4. Applying the expression language to device attributes in a multi-entity scenario