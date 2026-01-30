import json
import mysql.connector
from dotenv import load_dotenv
import os

# Whitelist of allowed table names for dynamic queries
ALLOWED_MASTER_TABLES = {
    'master_model', 'master_capacity', 'master_glass', 'master_ndt',
    'master_temperature', 'master_pressure', 'master_agitator_type',
    'master_drive_shaft_type', 'master_jacket_type', 'master_support',
    'master_jacket_ndt', 'master_material_shell_jacket', 'master_material_nozzle_jacket',
    'master_material_earthing', 'master_drive_shaft_make', 'master_drive_shaft_housing',
    'master_drive_shaft_sealing', 'master_drive_shaft_inborad', 'master_drive_shaft_outborad',
    'master_drive_gear_make', 'master_drive_gear_type', 'master_drive_motor_make',
    'master_drive_motor_mounting', 'master_drive_motor_type_1', 'master_drive_motor_type_2',
    'master_drive_hp', 'master_material_gasket', 'master_material_fasteners_pressure',
    'master_material_split'
}

class OFNDB:
    def __init__(self):
          self.connection = self.connect_to_db()

    def connect_to_db(self):
        # Load environment variables from .env file
        load_dotenv()

        # Retrieve credentials from environment
        host = os.getenv('HOST')
        user = os.getenv('USER')
        password = os.getenv('PASSWORD')

        # Connect to MySQL
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database='ofn'
        )
        return connection

    def get_by_sfon(self, sfon):
        try:
            # Create a cursor to execute SQL queries
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("USE ofn")
            # Execute the SQL script to create the database and tables
            try:
                vessel_query = "SELECT * FROM vessel_history WHERE sfon_no = %s ORDER BY CAST(rev AS SIGNED) DESC LIMIT 1"
                cursor.execute(vessel_query, (sfon,))
                # Fetch all results
                rows = cursor.fetchall()
                vessel_details = None
                if len(rows) > 0:
                    vessel_details = rows[0]

                    cursor.execute("SELECT name FROM master_model WHERE id = %s", (vessel_details['model_id'],))
                    reactor = cursor.fetchall()
                    vessel_details['reactor'] = reactor[0]['name']

                    cursor.execute("SELECT name FROM master_capacity WHERE id = %s", (vessel_details['reactor_id'],))
                    model = cursor.fetchall()
                    vessel_details['model'] = model[0]['name']

                    cursor.execute("SELECT name FROM master_glass WHERE id = %s", (vessel_details['glass_id'],))
                    glass = cursor.fetchall()
                    vessel_details['glass'] = glass[0]['name']

                    cursor.execute("SELECT name FROM master_ndt WHERE id = %s", (vessel_details['ndt'],))
                    ndt = cursor.fetchall()
                    vessel_details['ndt_value'] = ndt[0]['name']

                    cursor.execute("SELECT name FROM master_temperature WHERE id = %s", (vessel_details['temperature'],))
                    design_temperature = cursor.fetchall()
                    vessel_details['design_temperature'] = design_temperature[0]['name']

                    cursor.execute("SELECT name FROM master_pressure WHERE id = %s", (vessel_details['pressure'],))
                    design_pressure = cursor.fetchall()
                    vessel_details['design_pressure'] = design_pressure[0]['name']

                    agitator_types_list = json.loads(vessel_details['agitator_type'])

                    agitator_types = []
                    for type_id in agitator_types_list:
                        if type_id is not None:
                            cursor.execute("SELECT name FROM master_agitator_type WHERE id = %s", (type_id,))
                            fetched_type = cursor.fetchall()
                            agitator_types.append(fetched_type[0]['name'])
                    vessel_details['agitator_flight_types'] = agitator_types

                    cursor.execute("SELECT * FROM master_drive_shaft_type WHERE id = %s", (vessel_details['agitator_d_shaft_type'],))
                    sealing_type = cursor.fetchall()
                    vessel_details['sealing_type'] = sealing_type[0]['name']

                    cursor.execute("SELECT name FROM master_jacket_type WHERE id = %s", (vessel_details['jacket_type'],))
                    jacket_type = cursor.fetchall()
                    vessel_details['jacketType'] = jacket_type[0]['name']

                    cursor.execute("SELECT name FROM master_pressure WHERE id = %s", (vessel_details['jacket_pressure'],))
                    jacket_pressure = cursor.fetchall()
                    vessel_details['jacketPressure'] = jacket_pressure[0]['name']

                    cursor.execute("SELECT name FROM master_support WHERE id = %s", (vessel_details['jacket_support'],))
                    jacket_support = cursor.fetchall()
                    vessel_details['jacketSupport'] = jacket_support[0]['name']

                    cursor.execute("SELECT name FROM master_temperature WHERE id = %s", (vessel_details['jacket_temperature'],))
                    jacket_temperature = cursor.fetchall()
                    vessel_details['jacketTemperature'] = jacket_temperature[0]['name']

                    cursor.execute("SELECT name FROM master_jacket_ndt WHERE id = %s", (vessel_details['jacket_ndt'],))
                    jacket_ndt = cursor.fetchall()
                    vessel_details['jacketNDT'] = jacket_ndt[0]['name']

                    cursor.execute("SELECT name FROM master_material_shell_jacket WHERE id = %s", (vessel_details['jacket_material_shell'],))
                    jacket_material = cursor.fetchall()
                    vessel_details['jacketMaterialShell'] = jacket_material[0]['name']

                    cursor.execute("SELECT name FROM master_material_nozzle_jacket WHERE id = %s", (vessel_details['jacket_material_nozzle'],))
                    nozzle_material = cursor.fetchall()
                    vessel_details['jacketMaterialNozzle'] = nozzle_material[0]['name']

                    cursor.execute("SELECT name FROM master_material_earthing WHERE id = %s", (vessel_details['material_earthing'],))
                    material_earthing_type = cursor.fetchall()
                    vessel_details['material_earthing_type'] = material_earthing_type[0]['name']

                    cursor.execute("SELECT name FROM master_drive_shaft_type WHERE id = %s", (vessel_details['agitator_d_shaft_type'],))
                    shaft_type = cursor.fetchall()
                    vessel_details['shaft_type'] = shaft_type[0]['name']

                    cursor.execute("SELECT name FROM master_drive_shaft_make WHERE id = %s", (vessel_details['agitator_d_shaft_make'],))
                    shaft_make = cursor.fetchall()
                    vessel_details['shaft_make'] = shaft_make[0]['name']

                    cursor.execute("SELECT name FROM master_drive_shaft_housing WHERE id = %s", (vessel_details['agitator_d_shaft_house'],))
                    shaft_housing = cursor.fetchall()
                    vessel_details['shaft_housing'] = shaft_housing[0]['name']

                    cursor.execute("SELECT name FROM master_drive_shaft_sealing WHERE id = %s", (vessel_details['agitator_d_shaft_seal'],))
                    shaft_sealing = cursor.fetchall()
                    vessel_details['shaft_sealing'] = shaft_sealing[0]['name']

                    cursor.execute("SELECT name FROM master_drive_shaft_inborad WHERE id = %s", (vessel_details['agitator_d_shaft_in'],))
                    shaft_inboard = cursor.fetchall()
                    vessel_details['shaft_inboard'] = shaft_inboard[0]['name']

                    if vessel_details['agitator_d_shaft_out'] is not None:
                        cursor.execute("SELECT name FROM master_drive_shaft_outborad WHERE id = %s", (vessel_details['agitator_d_shaft_out'],))
                        shaft_outboard = cursor.fetchall()
                        vessel_details['shaft_outboard'] = shaft_outboard[0]['name']
                    else:
                        vessel_details['shaft_outboard'] = None

                    if vessel_details['agitator_d_shaft_other'] is not None:
                        cursor.execute("SELECT name FROM master_drive_shaft_outborad WHERE id = %s", (vessel_details['agitator_d_shaft_other'],))
                        shaft_other = cursor.fetchall()
                        vessel_details['shaft_other'] = shaft_other[0]['name']
                    else:
                        vessel_details['shaft_other'] = None

                    # agitator_d_gear_make
                    cursor.execute("SELECT name FROM master_drive_gear_make WHERE id = %s", (vessel_details['agitator_d_gear_make'],))
                    gear_make = cursor.fetchall()
                    vessel_details['gear_make'] = gear_make[0]['name']

                    # agitator_d_gear_type
                    cursor.execute("SELECT name FROM master_drive_gear_type WHERE id = %s", (vessel_details['agitator_d_gear_type'],))
                    gear_type = cursor.fetchall()
                    vessel_details['gear_type'] = gear_type[0]['name']

                    # agitator_d_motor_make
                    cursor.execute("SELECT name FROM master_drive_motor_make WHERE id = %s", (vessel_details['agitator_d_motor_make'],))
                    motor_make = cursor.fetchall()
                    vessel_details['motor_make'] = motor_make[0]['name']

                    # agitator_d_motor_mounting
                    cursor.execute("SELECT name FROM master_drive_motor_mounting WHERE id = %s", (vessel_details['agitator_d_motor_mounting'],))
                    motor_mounting = cursor.fetchall()
                    vessel_details['motor_mounting'] = motor_mounting[0]['name']

                    # agitator_d_motor_type_1
                    cursor.execute("SELECT name FROM master_drive_motor_type_1 WHERE id = %s", (vessel_details['agitator_d_motor_type_1'],))
                    motor_standard = cursor.fetchall()
                    vessel_details['motor_standard'] = motor_standard[0]['name']

                    # agitator_d_motor_type_2
                    cursor.execute("SELECT name FROM master_drive_motor_type_2 WHERE id = %s", (vessel_details['agitator_d_motor_type_2'],))
                    motor_type = cursor.fetchall()
                    vessel_details['motor_type'] = motor_type[0]['name']

                    # v_agitator_d_motor_hp
                    cursor.execute("SELECT name FROM master_drive_hp WHERE id = %s", (vessel_details['v_agitator_d_motor_hp'],))
                    motor_hp = cursor.fetchall()
                    vessel_details['motor_hp'] = motor_hp[0]['name']

                    # master_material_gasket -> material_gasket
                    cursor.execute("SELECT name FROM master_material_gasket WHERE id = %s", (vessel_details['material_gasket'],))
                    gasket = cursor.fetchall()
                    vessel_details['gasket'] = gasket[0]['name']

                    # master_material_fasteners_pressure -> material_fasteners
                    cursor.execute("SELECT name FROM master_material_fasteners_pressure WHERE id = %s", (vessel_details['material_fasteners'],))
                    fastener = cursor.fetchall()
                    vessel_details['fastener'] = fastener[0]['name']

                    # master_material_split -> material_split
                    cursor.execute("SELECT name FROM master_material_split WHERE id = %s", (vessel_details['material_split'],))
                    split_flange = cursor.fetchall()
                    vessel_details['split_flange'] = split_flange[0]['name']

                    print("Successfully fetched.")

                return vessel_details

            except mysql.connector.Error as err:
                print(f"Error: {err}")
            finally:
                cursor.close()
        except Exception as e:
            print(f"Error while fetching data from table: {e}")

    def get_masters(self, data):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("USE ofn")
            try:
                model_info = data['model_info']
                model_id = model_info['modelId']
                reactor_id = model_info['reactorId']

                cursor.execute("SELECT id FROM master_capacity WHERE capacity = %s AND name = %s",
                              (model_info['capacity'], model_info['model']))
                rows = cursor.fetchall()
                capacity_id = rows[0]['id']

                masters = list(data['masters'].keys())
                for master in masters:
                    if master == 'component':
                        continue
                    if master == 'master_jacket_type':
                        cursor.execute("SELECT name FROM master_jacket_type WHERE capacity_id = %s AND status = '1'", (capacity_id,))
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_temperature':
                        cursor.execute("SELECT name FROM master_temperature WHERE model_id = %s", (reactor_id,))
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_pressure':
                        cursor.execute("SELECT name FROM master_pressure WHERE model_id = '1'")
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_jacket_ndt':
                        cursor.execute("SELECT name FROM master_jacket_ndt WHERE capacity_id = '1'")
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_drive_hp':
                        cursor.execute("SELECT name FROM master_drive_hp WHERE capacity_id = %s", (capacity_id,))
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_material_gasket':
                        cursor.execute("SELECT name FROM master_material_gasket WHERE status = '1'")
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_material_fasteners_pressure':
                        cursor.execute("SELECT name FROM master_material_fasteners_pressure WHERE status = '1'")
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_material_split':
                        cursor.execute("SELECT name FROM master_material_split WHERE status = '1'")
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    else:
                        # Validate table name against whitelist to prevent SQL injection
                        if master in ALLOWED_MASTER_TABLES:
                            # Table name cannot be parameterized, but we've validated it against whitelist
                            cursor.execute(f"SELECT name FROM {master}")
                            rows = cursor.fetchall()
                            data['masters'][master] = rows
                        else:
                            print(f"Warning: Attempted query on non-whitelisted table: {master}")
                            data['masters'][master] = []
                return data
            except mysql.connector.Error as err:
                print(f"Error: {err}")
            finally:
                cursor.close()
        except Exception as e:
            print(f"Error while fetching data from table: {e}")
