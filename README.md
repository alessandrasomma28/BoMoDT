# BoMoDT: Bologna Mobility Digital Twin

![Python Version](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/alessandrasomma28/MOBIDT/refs/heads/main/images/badges/pythonb.json&label=Python&query=$.python.version&color=blue&cacheSeconds=60&logo=python)
![License](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/alessandrasomma28/MOBIDT/refs/heads/main/images/badges/license.json&label=License&query=$.license.version&color=orange&cacheSeconds=60&logo=GNU)
![Repo Size](https://img.shields.io/github/repo-size/alessandrasomma28/MOBIDT?logo=github)
![GitHub release](https://img.shields.io/github/v/release/alessandrasomma28/MOBIDT?logo=github)
![SUMO](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/alessandrasomma28/MOBIDT/refs/heads/main/images/badges/sumob.json&label=SUMO&query=$.sumo.version&color=green&cacheSeconds=60&logo=eclipse)


BoMoDT is the *Mobility Digital Twin* (MoDT) platform designed for the Italian City of *Bologna* (Bo). Developed 
following a *Model-Driven Architecture* (MDA) approach and using automatized model-to-model transformations [**MoDT-M2M-MTT**](https://anonymous.4open.science/r/MoDT-M2M-TT/README.md) tool, BoMoDT is based on *open-source data* retrieved from the Municipality of Bologna and *open-source technologies*, i.e., **FIWARE** for data management and data interoperability and **Eclipse Simulator of Urban MObility** (SUMO) for traffic conditions modeling and simulations.

The BoMoDT platform provides:

1. Digital **representation** and state **simulation** to model the structural and behavioral aspects of Bologna's infrastructure and simulate traffic scenarios.  
   - [*Eclipse SUMO*](https://eclipse.dev/sumo/) is utilized for traffic modeling and simulation.

2. **Bidirectional synchronization** to enable data flow from physical sensors to the Digital Twin and feedback from the Digital Twin to physical traffic light systems.  
   - [*FIWARE Generic Enablers*](https://www.fiware.org/catalogue/) (GEs) facilitate data exchange and management between the real system and its Digital Twin, ensuring semantic data interoperability.

3. **Traffic monitoring** to observe current traffic flow and stay updated on the state of Bologna City as well as simulation results based on dynamically generated scenarios.  
   - A [*Django WebApp*](https://www.djangoproject.com/), combined with a [*Grafana*](https://grafana.com/) dashboard, is implemented to:  
     *(i)* monitor the state of context entities modeled with FIWARE Smart Data Models,  
     *(ii)* track traffic flow patterns using the Grafana Dashboard, and  
     *(iii)* visualize simulation results after the simulation is completed.

     
## BoMoDT Architecture Overview 
The architecture of the BoMoDT platform is depicted in Figure 1. This diagram offers a simplified overview of the platform's design to facilitate better understanding. Detailed information about each component can be found in their respective folders.
The BoMoDT platform incorporates *open-source data* from the following sources:
* [**Bologna Open Data**](https://opendata.comune.bologna.it/):  Real traffic data from Bologna are collected. For more information, refer to the [*data README*](https://github.com/alessandrasomma28/MOBIDT/blob/main/data/README.md)
* [**OpenStreetMap**](https://www.openstreetmap.org/): The platform retrieves Bologna's road network layout and 
  additional infrastructure details, such as induction loops and traffic lights. For more information, refer to the 
  [*OSM README*](https://github.com/alessandrasomma28/MOBIDT/blob/main/sumoenv/README.md)

<div align="center">
  <img src="images/BoMoDTArchitecture.png" alt="Bologna Image" width="500"/>
  <p><b>Figure 1:</b> BoMoDT Architecture. </p>
</div>

The modules involved in BoMoDT are as follows:

1. **Bologna Mobility Virtual Environment (MVENV)**: This module was introduced because direct access to Bologna's 
   real infrastructure is not feasible. As a result, BoMoDT incorporates an emulator of Bologna's traffic data streams 
   capable of executing control commands for adaptive traffic light management.  As a result, BoMoDT incorporates an 
   emulator to ensure the presence of a continuously running physical counterpart in a Digital Twin context. Further details at [*BOLOGNA MVENV README*](https://github.com/alessandrasomma28/MOBIDT/tree/main/mobilityvenv)

2. **FIWARE** [**Orion-LD Context Broker**](https://github.com/FIWARE/context.Orion-LD): This is the mandatory 
   component in any "powered by FIWARE" smart solution. It is responsible for managing context entities in compliance 
   with the *Next Generation Service Interface* (NGSI) protocol in Linked Data (LD) version. The current context 
   entities' state is stored in a **Mongo** database. Further details at [*FIWARE VENV README*](https://github.com/alessandrasomma28/MOBIDT/blob/main/fiwareenv/README.md)

3. **FIWARE** [**IoT Agent - JSON**](https://github.com/telefonicaid/iotagent-json): This is the Internet of Things 
Agent (IOTA) for JSON-based protocols (with AMQP, HTTP, and MQTT transports). This IoT Agent acts as a bridge between 
JSON and the NGSI interface of the context broker, converting device-specific protocols into the NGSI standard. 
Devices sending measurements or receiving commands must be registered beforehand. Further details at [*FIWARE VENV 
README*](https://github.com/alessandrasomma28/MOBIDT/blob/main/fiwareenv/README.md)

4. **FIWARE** [**QuantumLeap**](https://quantumleap.readthedocs.io/en/latest/): This is a time-based 
   data-persistence Generic Enabler subscribed to context updates, for storing and querying time-series data in 
   **Timescale**. QuantumLeap addresses the inherent limitation of the Context Broker, which only stores the current 
   state. Further details at [*FIWARE VENV README*](https://github.com/alessandrasomma28/MOBIDT/blob/main/fiwareenv/README.md)

5. **Eclipse SUMO**: This is microscopic multi-modal traffic simulator that modeling individual road users, 
   including cars, buses, and pedestrians, enabling detailed analysis of traffic phenomena like congestion and 
   emissions. Simulation data inputs and outputs are locally stored. Further details at [*SUMO README*](https://github.com/alessandrasomma28/MOBIDT/blob/main/sumoenv/README.md)

6. The **Digital Shadow Manager**, **Planner & Scenario Generator**, and **Digital Twin Manager** are key Python 
   modules available in [**libraries**](https://github.com/alessandrasomma28/MOBIDT/tree/main/libraries). These modules are responsible for generating digital shadows (temporal data traces), creating and executing simulation scenarios, planning actions to be performed in the physical system, and orchestrating the overall Digital Twin system, respectively. 


7. **Django WebApp & Grafana Dashboard** provides a user interface for monitoring (i) context entities modeled with FIWARE Smart Data Models, real-time traffic flow patterns, and simulation results.

### Device Compatibility
The BoMoDT platform is deployed and tested on a Windows device. Its compatibility with Linux and macOS devices depends on the underlying technologies supporting the platform. While FIWARE is fully containerized and can potentially be adapted to other environments, the Eclipse SUMO compatibility should be verified by consulting the [*Eclipse Documentation*](https://sumo.dlr.de/docs/Installing/index.html).

<div align="center">
  <img src="images/BoMoDTDeploy.png" alt="Bologna Image" width="350"/>
  <p><b>Figure 2:</b> BoMoDT UML Deployment Diagram. </p>
</div>

BoMoDT consists of three execution environments:

1. **Docker Environment** provides a containerized infrastructure for deploying FIWARE components, including IoT Agent JSON, Orion-LD, and QuantumLeap, along with MongoDB for current data storage and TimescaleDB for historical data storage. Additionally, Grafana is containerized and available for independent visualization and monitoring, separate from the Django WebApp.

2. **Eclipse Simulator Engine** is responsible for performing urban mobility simulations.

3. **Python Virtual Environment** hosts the Python modules generated through the MDA-based approach, alongside additional modules developed to implement and execute the Bologna MVENV.


## BoMoDT Repository Structure



## BoMoDT Platform Execution

The **BoMoDT** platform can be executed either manually via the command line or by using the provided bash script 
(for Windows OS) included in the repository. Below are the detailed steps to deploy and execute the BoMoDT platform.

### Prerequisites
Before executing the **BoMoDT** platform, ensure the following prerequisites are installed and properly configured on your system:

- **Python >= 3.12**: Required to execute the core scripts and manage the environment. Install the latest version 
  from  [Python.org](https://www.python.org/downloads/).
- **Eclipse SUMO 1.19**: Necessary for traffic modeling and simulation. Download and install from [Eclipse SUMO]
  (https://www.eclipse.org/sumo/).
- **Docker and Docker Compose**: Required to deploy the FIWARE environment and associated components. Install the 
  latest versions from [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/).
- **Git**: Needed to clone the repository. Install Git from [Git SCM](https://git-scm.com/).
- **System Requirements**: Sufficient disk space and computational power to run Docker containers, execute Eclipse 
  simulator and store simulation results.

Ensure all the above dependencies are installed and available in your system's `PATH` before proceeding with the 
setup and execution of the platform.

---

### Deployment and Execution from Command Line
1. Clone the repository to your local machine:
   ```bash
   git clone repository-url
   ```
2. Navigate to the repository directory:
    ```bash
   cd /path/to/repository/BoMoDT
   ```

#### FIWARE Environment Setup
After cloning the repository, the FIWARE environment must be activated to enable required components.
1. Navigate to the fiwareenv directory:
    ```bash
   cd /path/to/repository/BoMoDT/fiwareenv
   ```
> Ensure that the following files are present in the fiwareenv directory: docker-compose.yml and .env

2. Deploy the required containers for Orion-LD, IoT Agent JSON, QuantumLeap, MongoDB, TimescaleDB, and Grafana by 
   running the following command:
    ```bash
   docker-compose up -d
   ```
Further details are provided in the folder [*README.md*](fiwareenv/README.md). 

#### MVENV and Python Environment Setup
Before running `main.py` script, a Python Virtual Environment must be activated. The environment can be created 
using the provided **requirements.txt** file. 

1. Create and activate a Python virtual environment in repository directory:
    1. If virtualenv is not installed in your local machine, install it by running:
   ```bash
   python3 -m pip install virtualenv
   ```
   2. Create a Python virtual environment:
   ```bash
   virtualenv venv
   ```
   3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Once the Python virtual environment has been created and activated, install the required Python packages using the 
   **requirements.txt**:
    ```bash
   pip3 install -r requirements.txt
   ```
3. Run the `main.py` script: 
   ```bash
   python3 main.py
   ```
> **Note**: Running this command will activate the Bologna MVENV, initiating data transmission to the Digital Twin 
> through FIWARE GEs. The simulation scenarios are automatically configured and executed in SUMO during this process.

#### Django WebApp and Grafana Dashboard
1. Navigate to webApp backend repository:
    ```bash
   cd path/to/repository/BoMoDT/udtBackEnd
   ```
2. Run the command: 
    ```bash
   python3 manage.py runserver
   ```

#### Eclipse SUMO Environment Setup
The **Eclipse SUMO Simulator** is utilized during the execution of the BoMoDT platform for modeling and simulating 
traffic scenarios. Additionally, Eclipse SUMO can be executed independently using the standalone configuration 
provided in the folder [*sumoenv/standalone*](sumoenv/standalone).

For detailed instructions on setting up and executing Eclipse SUMO, refer to the [*README.md*](sumoenv/README.md) 
file located in the `sumoenv` folder.

---

### Deployment and Execution for Windows OS
The [`setup.bat`](setup.bat) script is provided for setting up the environment and running the application.

#### Prerequisites

- **Docker**: Ensure Docker is running before executing the script. If Docker is not active, the script will terminate.
- **Python Virtual Environment (venv)**: A Python virtual environment must be created beforehand, either using the  
  steps outlined earlier or by setting it up in your preferred IDE (e.g., PyCharm, VSCode, etc.). The script will 
  abort if no virtual environment is detected.

#### Script Workflow
The `setup.bat` script performs the following steps:
1. Creates the required Docker containers.
2. Activates the Python virtual environment.
3. Verifies that the virtual environment is correctly activated.
4. Runs the Django web application.
5. Executes the `main.py` script to initialize and run the MVENV.

#### Usage
Run the script by executing:

```bash
setup.bat
```
or double clicking on `setup.bat` file. 










