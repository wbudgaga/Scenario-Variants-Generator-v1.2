# Scalable Server
Developing a scalable server that relies on thread pool and Non-blocking I/O to handle high network traffic. The implementation includes two components, a server and multiple clients (minimum 100 clients). The server accepts incoming network connections from the clients, receives incoming traffic from these connections, and responds to the clients in the order of received messages by sending back the hash codes of the received messages. Each client connects and maintains an active connection to the server, sends a message including random content of size 8KB R times in a second, and tracks the sent messages by comparing their hash codes with the ones received from the server.

# Scenario Variants Generator
The framework was developed to generate variants for a given scenario. 
A scenario uses a large number of input parameters to describe disease properties and information about herds and their interactions with the environment. Generating a scenario variant involves randomly varying the values of the input parameters in their plausible ranges. For producing plausible ranges of the input parameters, the framework consults historical data that are available in previous scenarios as a preliminary step. The framework orchestrates the process of variants generation on multiple machines in parallel to enable generating a large number of variants in a relatively short time. The following Figure shows the inputs and the outputs of the framework: 

<p align="center">
<img width="431" alt="The variants generator framework" src="https://user-images.githubusercontent.com/40745827/86494017-ee298600-bd30-11ea-9cc8-3e2452a374b2.png">
</p>

The input parameters can be defined as simple data types (such as numerical data types) or complex types (such as probability density functions [PDFs] and charts). 
One of the challenges is that the framework has to automatically identify the types of the input parameters and vary the values of these parameters in their plausible ranges. For example, the following figure shows different PDFS that were used to describe the “cattle latent period” parameter in previous scenarios.

<p align="center">
<img width="431" alt="variousDistributions" src="https://user-images.githubusercontent.com/40745827/86493835-4744ea00-bd30-11ea-93be-719f85d89c51.png">
</p>

The framework uses the historical ranges to create a plausible range (bounding box) for each numerical variable and sample from the plausible ranges to vary the original values. The historical ranges are shrunk to become closer to and around the variables’ values being varied. The bounding boxes enable generating scenario variants in the neighborhood of the input space of the original scenario. For input parameters that are defined as PDFs, the framework converts each PDF into 5 numerical values (minimum value of x, maximum value of x, mean, variance, skewness) that describe the distribution characteristic, finds the plausible ranges for the 5 numerical values, varies the 5 values in their plausible ranges, uses the varied values to construct the varied version of the PDF. The framework supports the following PDFs:

<p align="center">
<img width="831" alt="Supported PDFs" src="https://user-images.githubusercontent.com/40745827/86631141-00066580-bf8b-11ea-8df3-d5da2e96c590.png">
</p>

The following figures show examples of input parameters of complex types and their variad versions:

<p align="center">
<img width="500" alt="Supported PDFs" src="https://user-images.githubusercontent.com/40745827/86643410-e882a900-bf99-11ea-81e4-29d6cc7ab48c.png">
</p>

To vary the values of the input parameters, the framework employes
Latin hypercube sampling (LHS) to sample from the plausible range. LHS
stratifies the input probability distributions to better represent their underlying variability. This reduces the number of samples that are required for the framework to adequately explore the scenario parameter space, which in turn decreases the overall computational footprint of the framework. The following figure shows a visual comparison of sampling performed over a normal distribution using random, Monte Carlo, and Latin hypercube sampling by generating 1,000 samples and representing them by 50 bins.


<p align="center">
<img width="431" alt="A visual comparison of unweighted, weighted, and Latin hypercube sampling" src="https://user-images.githubusercontent.com/40745827/86634860-a0f71f80-bf8f-11ea-9e86-5a9a8035073e.png">
</p>

For generating the variants, the framework performs multiple tasks as they are shown in the following figure:


<p align="center">
<img width="831" alt="The workflow of variants generation process" src="https://user-images.githubusercontent.com/40745827/86634178-c6cff480-bf8e-11ea-8b07-c6300be7c1c7.png">
</p>
