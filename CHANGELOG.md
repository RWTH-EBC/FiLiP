### v.0.2.4
- fixed ContextAttribute: wrong type conversion for value ([#173](https://github.com/RWTH-EBC/FiLiP/issues/173))

#### v0.2.3
- added `override_metadata` argument according to new metadata update semantics in orion (https://fiware-orion.readthedocs.io/en/master/user/metadata.html#updating-metadata) ([#157](https://github.com/RWTH-EBC/FiLiP/issues/157))
- fixed test for patch_entity ([#157](https://github.com/RWTH-EBC/FiLiP/issues/157))
- added flag to ntoify only changed attributes ([#154](https://github.com/RWTH-EBC/FiLiP/issues/154))
- fixed issue of client generation when multiple clients are required ([#151](https://github.com/RWTH-EBC/FiLiP/issues/151))
- fixed throttling=0 is not working when posting a subscription ([#148](https://github.com/RWTH-EBC/FiLiP/issues/148))
- added filter functions for better subscription handling ([#141](https://github.com/RWTH-EBC/FiLiP/issues/141))
- added filter functions for better device handling ([#143](https://github.com/RWTH-EBC/FiLiP/issues/143))
- fixed coupled delete of devices and entities ([#143](https://github.com/RWTH-EBC/FiLiP/issues/143))
- Add images to tutorials ([#139](https://github.com/RWTH-EBC/FiLiP/issues/139))

#### v0.2.2
- Updated requirements for tutorials ([#132](https://github.com/RWTH-EBC/FiLiP/issues/132))
- fixed quantumleap timeseries header ([#133](https://github.com/RWTH-EBC/FiLiP/issues/133))
- fixed broken imports for tutorials ([#134](https://github.com/RWTH-EBC/FiLiP/issues/134))

#### v0.2.1
- Updated documentation ([#128](https://github.com/RWTH-EBC/FiLiP/issues/128))
- Improve tutorials ([#127](https://github.com/RWTH-EBC/FiLiP/issues/127))

#### v0.2.0
- Refactored units model ([#107](https://github.com/RWTH-EBC/FiLiP/issues/107))
- Updated and moved data model generator ([#117](https://github.com/RWTH-EBC/FiLiP/issues/117))
- quantumleap subscription missing ql_url ([#108](https://github.com/RWTH-EBC/FiLiP/issues/108))
- Fixed lazy attributes in IoTA Device model ([#105](https://github.com/RWTH-EBC/FiLiP/issues/105))
- Added get_commands to ContextEntity model ([#87](https://github.com/RWTH-EBC/FiLiP/issues/87))
- Added missing attribute requets for context broker ([#113](https://github.com/RWTH-EBC/FiLiP/issues/113))
- Fixed broken attribute mapping in IoTAMQTTClient ([#122](https://github.com/RWTH-EBC/FiLiP/issues/122))
- Added tutorials ([#111](https://github.com/RWTH-EBC/FiLiP/issues/111))
- Updated documentation ([#151](https://github.com/RWTH-EBC/FiLiP/issues/51))

#### v0.1.8
- QuantumLeap request pagination ([#47](https://github.com/RWTH-EBC/FiLiP/issues/47))
- introduce mqtt client ([#45](https://github.com/RWTH-EBC/FiLiP/issues/45))
- introduce concurrent testing and clean up utils([#41](https://github.com/RWTH-EBC/FiLiP/issues/41))
- include default values in subscription update ([#39](https://github.com/RWTH-EBC/FiLiP/issues/39))
- move back to more simple docs design ([#32](https://github.com/RWTH-EBC/FiLiP/issues/32))
- added MQTT notifications ([#24](https://github.com/RWTH-EBC/FiLiP/issues/24))
- introduced [CHANGELOG.md](https://github.com/RWTH-EBC/FiLiP/blob/development/CHANGELOG.md) with versions
- semantic model features [#30](https://github.com/RWTH-EBC/FiLiP/issues/30)
- remodeled ngsi-v2 models ([#58,#59,#60](https://github.com/RWTH-EBC/FiLiP/issues/60))
- improved ContextEntity and Device deleting methods ([#27](https://github.com/RWTH-EBC/FiLiP/issues/28))
- patch methods for ContextEntity and Device ([#74](https://github.com/RWTH-EBC/FiLiP/issues/74))
- refactored and improved Examples ([#90](https://github.com/RWTH-EBC/FiLiP/issues/90))

#### v0.1.7
- introduced automatic testing
([#18](https://github.com/RWTH-EBC/FiLiP/issues/18))

#### v0.1.0
- Completely reworked the structure of the library
- Added documentation  
- Use Pydantic for model validation and parsing
- Added unittests
- Configuration via environment variables, json or local
- Moved to github.com/RWTH-EBC
- Bugfix
