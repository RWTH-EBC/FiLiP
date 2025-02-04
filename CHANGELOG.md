### v0.6.x
- add: Tutorial for saving live timeseries data (e.g., forecast) in context broker and timeseries database ([#336](https://github.com/RWTH-EBC/FiLiP/pull/363))
- add: Tutorial for using session object ([#370](https://github.com/RWTH-EBC/FiLiP/pull/370))
- fix: Addition of trailing slash if missing from base url ([#371](https://github.com/RWTH-EBC/FiLiP/pull/371))
- fix: Serialization error for custom datamodels during batch operation ([#376](https://github.com/RWTH-EBC/FiLiP/pull/376))
- update: omit invalid entities in `get_entity_list` ([#375](https://github.com/RWTH-EBC/FiLiP/pull/375))

### v0.6.0
- add: Tutorial for connecting with secured endpoints ([#319](https://github.com/RWTH-EBC/FiLiP/pull/319))
- add: Example for notification based command ([#332](https://github.com/RWTH-EBC/FiLiP/pull/332))
- add: tests for clear functions ([#336](https://github.com/RWTH-EBC/FiLiP/pull/336))
- 🚀 **add: API client for NGSI-LD context broker** ([#338](https://github.com/RWTH-EBC/FiLiP/pull/338)
,[#356](https://github.com/RWTH-EBC/FiLiP/pull/356)
,[#327](https://github.com/RWTH-EBC/FiLiP/pull/327)
,[#300](https://github.com/RWTH-EBC/FiLiP/pull/300)
,[#301](https://github.com/RWTH-EBC/FiLiP/pull/301)
,[#212](https://github.com/RWTH-EBC/FiLiP/pull/212)
,[#222](https://github.com/RWTH-EBC/FiLiP/pull/222)
,[#221](https://github.com/RWTH-EBC/FiLiP/pull/221)
  )
- fix: clear functions for context broker ([#336](https://github.com/RWTH-EBC/FiLiP/pull/336))
- fix: validation error of ``ngsipayloadattr`` when the attribute substitution is used([#351](https://github.com/RWTH-EBC/FiLiP/pull/351))
- update: integrate the key-values endpoints with normalized endpoints ([#318](https://github.com/RWTH-EBC/FiLiP/pull/318))
- remove: ``update_entity_attributes_key_values`` and ``update_entity_key_values`` are removed ([#318](https://github.com/RWTH-EBC/FiLiP/pull/318))


### v0.5.0
- update: allow duplicated name in device, check uniqueness of object_id ([#279](https://github.com/RWTH-EBC/FiLiP/pull/279))
- update: upgrade dependency of `paho-mqtt` to v2 ([#273](https://github.com/RWTH-EBC/FiLiP/pull/273/))
- add: `json` and `ngsi` as payload format in custom notification model ([#296](https://github.com/RWTH-EBC/FiLiP/pull/296))
- add: support alterationTypes in subscription model ([#293](https://github.com/RWTH-EBC/FiLiP/pull/293))
- add: validation for JEXL based expression ([#260](https://github.com/RWTH-EBC/FiLiP/pull/260))
- add: tutorials for multi-entity ([#260](https://github.com/RWTH-EBC/FiLiP/pull/260))
- add: add ``update_entity_relationships`` to allow relationship update ([#271](https://github.com/RWTH-EBC/FiLiP/pull/271))
- add: timeseries query with all attrs and specific attr name ([#16](https://github.com/RWTH-EBC/FiLiP/pull/16))
- add: flag to determine the deletion of registration when clearing the CB ([#267](https://github.com/RWTH-EBC/FiLiP/pull/267))
- add: ``covered`` flag in notification model ([#310](https://github.com/RWTH-EBC/FiLiP/pull/310))
- fix: rework tutorials for pydantic v2 ([#259](https://github.com/RWTH-EBC/FiLiP/pull/259))
- fix: inconsistency of `entity_type` as required argument ([#188](https://github.com/RWTH-EBC/FiLiP/pull/188))
- fix: allow empty string in attribute value validation ([#311](https://github.com/RWTH-EBC/FiLiP/pull/311))

BREAKING CHANGE: upgrade dependency of `paho-mqtt` to v2 ([#273](https://github.com/RWTH-EBC/FiLiP/pull/273/))

### v0.4.1
- fix: Session added as optional parameter to enable tls communication with clients ([#249](https://github.com/RWTH-EBC/FiLiP/pull/249))
- fix: add missing package ``geojson_pydantic`` in setup.py ([#276](https://github.com/RWTH-EBC/FiLiP/pull/276))
- add: support entity creation with keyvalues ([#264](https://github.com/RWTH-EBC/FiLiP/pull/264))

#### v0.4.0
- add tutorial for protected endpoint with bearer authentication ([#208](https://github.com/RWTH-EBC/FiLiP/issues/208))
- add internal mqtt url for unittests @djs0109 ([#239](https://github.com/RWTH-EBC/FiLiP/pull/239))
- fix: compare subscriptions to prevent duplicated notifications @FWuellhorst, @RCX112 ([#138](https://github.com/RWTH-EBC/FiLiP/pull/138))
- update pandas version to `~=2.1.4` for `python>=3.9` ([#231](https://github.com/RWTH-EBC/FiLiP/pull/231))
- fix: wrong msg in iotac post device ([#214](https://github.com/RWTH-EBC/FiLiP/pull/214))
- add support to update entities with keyValues @djs0109 ([#245](https://github.com/RWTH-EBC/FiLiP/pull/245))
- add function to override the existing entity ([#232 ](https://github.com/RWTH-EBC/FiLiP/pull/232 ))
- fix: remove root slash from paths ([#251](https://github.com/RWTH-EBC/FiLiP/issues/251))
- fix: include headers in some requests ([#250](https://github.com/RWTH-EBC/FiLiP/issues/250))
- add: `forcedUpdate` and missing `overrideMetadata` in request parameters ([#236](https://github.com/RWTH-EBC/FiLiP/pull/236))
- feat: make context-entity more customizable ([#225](https://github.com/RWTH-EBC/FiLiP/issues/225))
- feat: add geojson support to context-entity ([#226](https://github.com/RWTH-EBC/FiLiP/issues/226))

BREAKING CHANGE:
- feat: make context-entity more customizable ([#225](https://github.com/RWTH-EBC/FiLiP/issues/225)) enforces stricter type validation as before. This might lead to errors in your code if you are not using the correct types. Please check the documentation for the correct types.

#### v0.3.0
- fix: bug in typePattern validation @richardmarston ([#180](https://github.com/RWTH-EBC/FiLiP/pull/180))
- add: add messages to all KeyErrors @FWuellhorst ([#192](https://github.com/RWTH-EBC/FiLiP/pull/192))
- add: optional module `semantics` in setup tool @djs0109
- fix: get() method of Units dose not work properly by @djs0109 ([#193](https://github.com/RWTH-EBC/FiLiP/pull/193))
- BREAKING CHANGE: Migration of pydantic v1 to v2 @djs0109 ([#199](https://github.com/RWTH-EBC/FiLiP/issues/199))

#### v0.2.5
- fixed service group edition not working ([#170](https://github.com/RWTH-EBC/FiLiP/issues/170))
- fixed service group can not be retrieved by apikey and resource ([#169](https://github.com/RWTH-EBC/FiLiP/issues/169))
- add new argument `strict_data_type` to entity.get_attributes to allow disabling the validator of data types ([#182](https://github.com/RWTH-EBC/FiLiP/issues/182))

#### v0.2.4
- fixed ContextAttribute: wrong type conversion for value ([#173](https://github.com/RWTH-EBC/FiLiP/issues/173))
- fixed Change does_entity_exists create error message if entity does not exist ([#167](https://github.com/RWTH-EBC/FiLiP/issues/167))
- fixed remove additional escape chars when sending a string ([#163](https://github.com/RWTH-EBC/FiLiP/issues/163))

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
