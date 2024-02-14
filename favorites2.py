import http.client
import json
from iw4x.iw4x_server import ServerList
def fetch_server_data(protocol: int = None) -> ServerList:
    # Debug print: Start of function
    print(f"Fetching server data (protocol={protocol})")
    # Define the host and path
    host = "iw4x.plutools.pw"
    path = "/v1/servers/iw4x"
    # Create a connection to the host
    conn = http.client.HTTPSConnection(host)
    query_params = {"protocol": protocol } if protocol else {}
    query = "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    url = path + query
    print(f"Requesting URL: {url}")
    # Make a GET request to the path
    conn.request("GET", url)
    # Get the response from the server
    response = conn.getresponse()
    # Debug print: Response received
    print(f"Response received with status code: {response.status}")
    # Read the response content
    data = response.read()
    # Close the connection
    conn.close()
    # Debug print: Connection closed
    print("Connection closed.")
    decoded_data = data.decode("utf-8")
    # Decode the response content and load it as JSON
    parsed_data = json.loads(decoded_data)
    # Debug print: Data parsed successfully
    print("Data parsed successfully.")
    servers = ServerList.from_dict(parsed_data)
    # Return the parsed data
    return servers

if __name__ == "__main__":
    try:
        # Fetch the server data
        servers = fetch_server_data()
        # sort servers by protocol
        servers.servers.sort(key=lambda x: x.protocol)
        for server in servers.servers:
            print(server)
    except Exception as e:
        # Print the exception details for debugging
        print(f"An error occurred: {e}")
        # Optionally, use pdb to enter the debugger
        import pdb; pdb.set_trace()
else: print(f"Imported as {__name__} from {__file__}")