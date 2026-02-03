import redis
import platform
import subprocess
import time

def connect(host, port, db=0):
	try:
		redis_client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
		if redis_client.ping():
			print("Connected to Redis successfully.")
		return redis_client
	except redis.ConnectionError:
		print("Failed to connect to Redis.")
		return None

def set_value_in_redis(redis_client, key, value):
	redis_client.set(key, value)
	print(f"Set key '{key}' with value '{value}' in Redis.")

def get_value_from_redis(redis_client, key):
	value = redis_client.get(key)
	print(f"Retrieved value for key '{key}' from Redis: {value}")
	return value

def launch_server(port):
	try:
		os_type = platform.system()
		process = None

		if os_type == "Linux" or os_type == "Darwin":  # macOS is "Darwin"
			# Check if redis-server command is available
			result = subprocess.run(["which", "redis-server"], capture_output=True, text=True)
			if result.returncode == 0:
				print(f"Launching Redis server on port {port}...")
				process = subprocess.Popen(["redis-server", "--port", str(port)])
				time.sleep(1)  # Allow some time for the server to start
				print(f"Redis server launched on Linux/macOS at port {port}.")
			else:
				print("Redis server not found. Please install Redis using your package manager.")

		elif os_type == "Windows":
			print("Detected Windows OS. Attempting to launch Redis using WSL.")
			try:
				process = subprocess.Popen(["wsl", "redis-server", "--port", str(port)])
				time.sleep(1)  # Allow some time for the server to start
				print(f"Redis server launched on Windows (WSL) at port {port}.")
			except FileNotFoundError:
				print("WSL or Redis server not found. Ensure WSL is installed, and Redis is available in your WSL environment.")

		else:
			print(f"Unsupported OS: {os_type}. Cannot start Redis server automatically.")

		return process

	except Exception as e:
		print(f"An error occurred while attempting to launch Redis: {e}")
		return None

# Main function for testing
def setup(address='localhost', port=6379):
	redis_process = None

	if address == 'localhost':
		redis_process = launch_server(port)

	redis_client = connect(address, port)

	if redis_client:
		set_value_in_redis(redis_client, "test_key", "test_value")
		get_value_from_redis(redis_client, "test_key")

	if redis_process:
		redis_process.terminate()
		print("Redis server terminated.")

if __name__ == "__main__":
	setup()
