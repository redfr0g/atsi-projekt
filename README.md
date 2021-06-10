# atsi-projekt
Path restoration (REST) method implementation for Floodlight SDN controller.

## Structure
* test.py - SDN test topology with few alternate links
* application.py - controller application that detects link fault and implements REST (restoration) method to restore routing
* flowpusher.py - script pushing initial static routing to flow tables

## Usage
1. Have Floodlight controller running.
2. Setup mininet `sudo python test.py`
3. Run the app first to gather full network topology `python3 application.py` 
4. Enable static routing between hosts `python flowpusher.py`
5. Simulate link malfunction with mininet CLI `link <switch1> <switch2> down`
6. :sunglasses:
