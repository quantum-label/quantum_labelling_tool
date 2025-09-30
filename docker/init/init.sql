SET FOREIGN_KEY_CHECKS=0;

INSERT INTO webapp_ehdscategory (name) VALUES
	 ('Access and provision'),
	 ('Coverage'),
	 ('Data documentation'),
	 ('Technical quality');
INSERT INTO webapp_dqdimension (name,definition,ehds_category_id,relevance) VALUES
	 ('Accessibility','Accessibility refers to the dataset being accompanied by clear and transparent access and usage conditions.',1,9.95),
	 ('Population coverage','Population coverage refers to the degree to which a dataset includes the potential eligible population.',2,6.47),
	 ('Population representativity','Population representativity refers to the degree to which the data adequately represent the population in question.',2,7.96),
	 ('Compliance','Compliance refers to the degree to which data has attributes that adhere to ethical standards, conventions, protocols or regulations.',3,7.46),
	 ('Data provenance','Data provenance means a description of the source of the data, including context, purpose, method and technology of data generation, documenting agents involved in the provenance of data, data validation routines, source data verification, traceability of changes, and quality control of data.',3,7.96),
	 ('Metadata scope','Metadata scope refers to the availability, comprehensiveness, level of detail of metadata and data dictionary that help users understand the data being used.',3,8.46),
	 ('Accuracy','Accuracy refers to the degree to which observations correctly describe what it was designed to measure.',4,9.95),
	 ('Coherence','Coherence is defined as the dimension that expresses how different parts of the dataset are uniform in their representation and meaning over time, such as formats, semantics (stability of the data models), and methods.',4,8.96),
	 ('Completeness','Completeness refers to the degree to which all information that could be available is present in a particular dataset organized as tabular data.',4,8.96),
	 ('Consistency','Consistency refers to the degree to which data has attributes that are plausible and are uniform with other data and over time.',4,9.95);
INSERT INTO webapp_dqdimension (name,definition,ehds_category_id,relevance) VALUES
	 ('Precision','Precision refers to the degree of approximation by which data can represent reality.',4,5.97),
	 ('Validity','Validity refers to the degree to which representations of data in a dataset conform to the specification of a data model or data models.',4,7.96);
INSERT INTO webapp_dqmetric (name,definition,additional_information,measurement_approach,formula,weight,dq_dimension_id,needs_report_URL) VALUES
	 ('Availability of a data access & usage policy','Availability of a data access & usage policy at the time of release of the dataset','HealthDCAT-AP access rights property refers to information that indicates whether the Dataset is open data, has access restrictions or is not public.','<a href="https://www.w3.org/TR/vocab-dcat/#Property:distribution_access_rights" target= "_blank">https://www.w3.org/TR/vocab-dcat/#Property:distribution_access_rights</a>','n/a',50.0,1,0),
	 ('Average time from data access application to data release','Average time from data access application to data release for a specific dataset','','The HDAB/data holder to provide the average using digital time-stamps for the process','n/a',50.0,1,0),
	 ('Coverage Rate','Coverage Rate (percentage of the eligible population represented in the dataset)','"Observed to expected methods suggested in the nominal group are fit for purpose.
HealthDCAT-AP POPULATION COVERAGE: This property provides a definition of the population within the dataset."','According to data holder information: (Number of individuals in the dataset / Total eligible population) x 100%','"(Number of individuals in the dataset / Total eligible population*) x 100%

(* according to data holder''s information)"',100.0,2,0),
	 ('Population representativity','How closely does the observed population represent the expected population?','Observed to expected methods suggested in the nominal group are fit for purpose.','According to data holder''s information.','n/a',100.0,3,0),
	 ('Documentation of compliance','Is there documentation of compliance with ethical standards, conventions, protocols or regulations?','','According to data holder''s information.','n/a',100.0,4,0),
	 ('Dataset source documentation','Is the source of the dataset documented?','','Ideally using a standard vocabulary as in DCAT-AP "dct:source; dct:creator; dct:contributor"','"dct:source
dct:creator
dct:contributor"',50.0,5,0),
	 ('Processes and operation documentation','Are the processes and operations on the data documented?','"PROV-DM ontology:
An agent is something that bears some form of responsibility for an activity taking place, for the existence of an entity, or for another agent''s activity.
An activity is something that occurs over a period of time and acts upon or with entities; it may include consuming, processing, transforming, modifying, relocating, using, or generating entities.
A derivation is a transformation of an entity into another, an update of an entity resulting in a new one, or the construction of a new entity based on a pre-existing entity."','Using PROV-O (PROV Ontology)','n/a',50.0,5,0),
	 ('Existence of comprehensive standardised metadata','Existence of comprehensive standardised metadata','','Link/reference to the standardised metadata model','n/a',40.0,6,0),
	 ('Existence of an exhaustive data dictionary at variable level','Existence of an exhaustive data dictionary at variable level','','Link/reference to the standardised vocabularies in the meta-data model. Note that what the data dictionary contains may depend on the type of data; in the case of non-structured data the data dictionary may include features on the data source, its components and its relationship with other data.','n/a',60.0,6,0),
	 ('Accuracy documentation','Is accuracy of the dataset documented?','"A report describing the external validation measures taken, such as:
- conformance of variables to known (externally measured) distributions
- conformance of variables to assumed value ranges of distributions
- steps to validate measurement accuracy of measured variables"','The report should provide information on steps done to validate measurement accuracy of measured variables; in addition it should, at variable level, provide information on conformance to known (externally measured) distributions or to assumed value ranges of distributions.','n/a',100.0,7,1);
INSERT INTO webapp_dqmetric (name,definition,additional_information,measurement_approach,formula,weight,dq_dimension_id,needs_report_URL) VALUES
	 ('Coherence documentation','Is coherence of the dataset documented?','A report outlining how the data has changed with respect to its meaning over time, such as formats, semantics (stability of the data models), and methods.','At dataset level, the report should contain information on the changes observed in formats, semantics (stability of the data models), and methods.','n/a',100.0,8,1),
	 ('Completeness documentation','Is completeness of the dataset documented?','"Using a framework or tools to generate variable level information of completeness in a quality report.

Completeness is typically measured for a single variable as:
n(null values*) / n(records)


*null values does not include explicit code values signifying that the information is not applicable or ""N/A""."','For each variable the dataset report should calculate the number of null values over the number of records. Explicit code values signifying that the information is not applicable are not considered null.','n/a',100.0,9,1),
	 ('Consistency documentation','Is consistency of the dataset documented?','"Using a framework or tools to generate variable level information of consistency in a quality report.

Consistency checks refer to variable level tests for:
- plausible range of numeric values
- codings are plausible in relation to one onother ""business logic"" tests
- use of valid codes (semantic)"','For each variable the dataset report should contain consistency checks that refer to, amongst others: plausible range of numeric values; codings are plausible in relation to one another - "business logic" tests; use of valid codes (semantic).','n/a',100.0,10,1),
	 ('Precision documentation','Is precision of the dataset documented?','"Using a framework or tools to generate variable level information of completeness in a quality report.

Presicion refers for example to:
- number of significant figures in numeric variables
- number of categories or ranges for grouped numeric variables
- number of categories/codes used for enumerated variables

A precondition is that the precision of variables is documented in the data dictionary."','"For each variable, the dataset report should contain computational checks including amongst others: granularity in numeric variables; number of categories or ranges for grouped numeric variables; number of categories/codes used for ordinal or nominal variables.
"','n/a',100.0,11,1),
	 ('Conformance report for the data model','Availability of a conformance report for the data model','"Using a framework or tools to generate variable level information of completeness in a quality report.

Validity or conformance checks refer to variable level tests for:
- data types (syntax)"','For each variable, the dataset report should contain computational checks for variable level syntax conformance (.i.e., conformance with expected syntax as per the data model)','n/a',100.0,12,1);

INSERT INTO webapp_dqcategoricalmetric (dqmetric_ptr_id) VALUES
	 (1),
	 (2),
	 (3),
	 (4),
	 (5),
	 (6),
	 (7),
	 (8),
	 (9),
	 (10);
INSERT INTO webapp_dqcategoricalmetric (dqmetric_ptr_id) VALUES
	 (11),
	 (12),
	 (13),
	 (14),
	 (15);
INSERT INTO webapp_dqcategoricalmetriccategory (dq_categorical_metric_id,text,value) VALUES
	 (1,'No policy available',0),
	 (1,'Basic policy available',1),
	 (1,'Comprehensive policy available',2),
	 (2,'More than 6 months',0),
	 (2,'3 to 6 months',1),
	 (2,'1 to 3 months',2),
	 (2,'Less than 1 month',3),
	 (3,'<80%: Limited coverage',0),
	 (3,'80-90%: Good coverage',1),
	 (3,'90-95%: Very good coverage',2);
INSERT INTO webapp_dqcategoricalmetriccategory (dq_categorical_metric_id,text,value) VALUES
	 (3,'95-100%: Near-universal or universal coverage',3),
	 (4,'No information on sampling methodology',0),
	 (4,'Sampling information does not demonstrate the sample representativity',1),
	 (4,'Sampling information demonstrates the sample representativity',2),
	 (4,'Dataset contains all expected population',3),
	 (5,'No.',0),
	 (5,'Documentation of applicable ethical standards, conventions, protocols or regulations, but no documentation of deviations or compliance.',1),
	 (5,'Documentation of applicable ethical standards, conventions, protocols or regulations, as well as documentation of deviations or compliance.',2),
	 (6,'No source is documented',0),
	 (6,'Source is documented',1);
INSERT INTO webapp_dqcategoricalmetriccategory (dq_categorical_metric_id,text,value) VALUES
	 (7,'No documentation on data processes and operations',0),
	 (7,'Some documentation on data processes and operations but not complying with PROV-O standards',1),
	 (7,'Full documentation on data processes and operations complying with PROV-O standards',2),
	 (8,'Non-standardised metadata',0),
	 (8,'Partially complying with standardised metadata model (e.g. HealthDCAT-AP)',1),
	 (8,'Fully complying with standardised metadata model (e.g. HealthDCAT-AP)',2),
	 (9,'No data dictionary',0),
	 (9,'Partial data dictionary: some variables described with basic information (i.e., names and brief definitions)',1),
	 (9,'Complete data dictionary: all variables described with detailed information (i.e., names, definitions, units, allowed values, etc.)',2),
	 (10,'Accuracy not documented',0);
INSERT INTO webapp_dqcategoricalmetriccategory (dq_categorical_metric_id,text,value) VALUES
	 (10,'Information on the efforts to ensure accuracy is provided (non statistical information provided)',1),
	 (10,'Statistical information on accuracy is provided at variable and/or individual level',2),
	 (11,'Coherence not documented',0),
	 (11,'Coherence documented for some entities, attributes and relations in the dataset',1),
	 (11,'Coherence documented for all entities, attributes and relations in the dataset',2),
	 (12,'Completeness not documented',0),
	 (12,'Some variables are analysed for completeness',1),
	 (12,'All variables are analysed for completeness',2),
	 (13,'Consistency not documented',0),
	 (13,'Consistency of some variables is documented',1);
INSERT INTO webapp_dqcategoricalmetriccategory (dq_categorical_metric_id,text,value) VALUES
	 (13,'Consistency of all variables is documented',2),
	 (14,'Precision not documented',0),
	 (14,'Precision of some variables is documented',1),
	 (14,'Precision of all variables is documented',2),
	 (15,'No report available',0),
	 (15,'Report available for validity of some variables',1),
	 (15,'Report available for validity of all variables',2);
INSERT INTO webapp_maturitydimension (name,definition) VALUES
	 ('Data collection process','The processes relating to the capture of data from multiple sources for secondary purposes'),
	 ('Data management - governance','The level of maturity of the data management processes'),
	 ('Data management - infrastructure','The level of implementation and development of the data holder''s data management infrastructure'),
	 ('Data provenance','Clear description of source and history of the dataset, providing a "transparent data pipeline"'),
	 ('Data access','How well defined and implemented are data access processes, from a legal, ethical and technical perspective'),
	 ('Data analytics environment','Analytical services, tooling and access to [secure] data environments'),
	 ('Data enhancement - augmentation','The application of various techniques to make data more useable for specific purposes'),
	 ('Data enhancement - enrichment','Data sources enriched for example with annotations, image labels, phenomes, derivations, NLP derived data labels'),
	 ('Data Model','Availability of clear, documented data model that provides structure and standardisation'),
	 ('Data Dictionary','Provided documented data dictionary and terminologies');
INSERT INTO webapp_maturitydimensionlevel (value,text,maturity_dimension_id) VALUES
	 (1,'No data collection or capture process for secondary purposes',1),
	 (2,'Ad hoc processes exist for data collection',1),
	 (3,'Defined processes exist for some data collection',1),
	 (4,'Defined processes exist for all data collection and are used for secondary purposes',1),
	 (5,'Processes are automated for all data collection, focus on continuous process improvement.',1),
	 (1,'No documented data management governance',2),
	 (2,'A documented data management plan covering collection, auditing, and management is available for the dataset',2),
	 (3,'Evidence that the data management plan has been implemented is available',2),
	 (4,'Demonstrated compliance with the data management plan',2),
	 (5,'Externally verified compliance with the data management plan',2);
INSERT INTO webapp_maturitydimensionlevel (value,text,maturity_dimension_id) VALUES
	 (1,'No data management infrastructure',3),
	 (2,'An emerging data management infrastructure, some validation and verification',3),
	 (3,'Data management infrastructure defined and confirmed as a standard process',3),
	 (4,'Data management infrastructure, with partially automated, verifed and validated [real time] data management',3),
	 (5,'A robust and comprehensive data management infrastructure, with fully automated, verifed and validated real time data management',3),
	 (1,'No documented provenance',4),
	 (2,'Source of the dataset is documented',4),
	 (3,'Source of the dataset and any transformations, rules and exclusions',4),
	 (4,'All original data items listed, all transformations, rules and exclusion listed and impact of these',4),
	 (5,'Ability to view earlier versions, including "raw" or "source" dataset, and review the impact of each stage/step',4);
INSERT INTO webapp_maturitydimensionlevel (value,text,maturity_dimension_id) VALUES
	 (1,'No data access processes or procedures',5),
	 (2,'Have the processes and procedures but don’t respond in timely and constistent manner',5),
	 (3,'Have the processes and procedures, and respond in timely and constistent manner',5),
	 (4,'Data access system that covers both technical and policy areas, in accordance with agreed metrics',5),
	 (5,'A comprehensive data access system that covers technical, ethical and policy areas (allowable uses, API documentation, access and approvals) compliant with EU Policy',5),
	 (1,'No data environment available',6),
	 (2,'Requested analysis can be undertaken by internal teams and provided back in anonymised format to data requestors',6),
	 (3,'The dataset can be used in a secure data environment (SDE)',6),
	 (4,'The dataset can be used in an SDE and other data and tools can be brought in as required',6),
	 (5,'The dataset can be used in federated organised environment',6);
INSERT INTO webapp_maturitydimensionlevel (value,text,maturity_dimension_id) VALUES
	 (1,'No data augmentation',7),
	 (2,'Some techniques to make data more useable for specific purposes',7),
	 (3,'Defined techniques to make data more useable for specific purposes',7),
	 (4,'Managed techniques to make data more useable for specific purposes',7),
	 (5,'Comprehensive application of various techniques and mapping to data model i.e. OMOP to make more useable for specific purposes',7),
	 (1,'The data has no additional derived fields, or enriched data.',8),
	 (2,'The data include additional derived fields, or enriched data.',8),
	 (3,'The data include additional derived fields, or enriched data used by other available data sources.',8),
	 (4,'The derived fields or enriched data were generated from, or used by, a peer reviewed algorithm.',8),
	 (5,'The data includes derived fields or enriched data from an [inter] national report.',8);
INSERT INTO webapp_maturitydimensionlevel (value,text,maturity_dimension_id) VALUES
	 (1,'There is no data model',9),
	 (2,'Known and accepted data model but some key field uncoded or free text',9),
	 (3,'Key fields codified using a local standard and updated over time',9),
	 (4,'Key fields codified using a national or international standard and updated',9),
	 (5,'Data Model conforms to an [inter] national standard and key fields codified using a national / international standard',9),
	 (1,'No Data Dictionary',10),
	 (2,'Data definitions available',10),
	 (3,'Definitions compiled into local data dictionary which is available online',10),
	 (4,'Dictionary relates to national definitions',10),
	 (5,'Dictionary is based on international standards and includes mapping',10);


SET FOREIGN_KEY_CHECKS=1;