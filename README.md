# Scenario Variants Generator
The framework was developed to generate variants for a given scenario. 
A scenario uses a large number of input parameters to describe disease properties and outbreak characteristics. Generating a scenario variant involves randomly varying the values of the input parameters in their plausible ranges. For producing plausible ranges of the input parameters, the framework consults historical data that are available in previous scenarios as a preliminary step. The framework orchestrates the process of variants generation on multiple machines in parallel to enable generating a large number of variants in a relatively short time. The following Figure shows the inputs and the outputs of the framework: 

<img width="431" alt="The variants generator framework" src="https://user-images.githubusercontent.com/40745827/86494017-ee298600-bd30-11ea-9cc8-3e2452a374b2.png">

The input parameters can be defined as simple data types (such as numerical data types) or complex types (such as probability density functions [PDFs] and charts. 
One of the challenges is that the framework has to automatically identify the types of the input parameters and vary the values of these parameters in their plausible ranges. For example, the following figure shows different PDFS that were used to describe the “cattle latent period” parameter in previous scenarios.

<img width="431" alt="variousDistributions" src="https://user-images.githubusercontent.com/40745827/86493835-4744ea00-bd30-11ea-93be-719f85d89c51.png">
