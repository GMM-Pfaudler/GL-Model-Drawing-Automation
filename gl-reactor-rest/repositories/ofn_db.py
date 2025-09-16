import json
import mysql.connector

class OFNDB:
    def __init__(self):
          self.connection = self.connect_to_db()
     
    def connect_to_db(self):
        # Define MySQL connection parameters
        host = 'KO-GMMPFW0046'  # or the IP address of your MySQL server
        user = 'root'  # replace with your MySQL username
        password = 'root'  # replace with your MySQL password

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
            cursor.execute(f"USE ofn")
            # Execute the SQL script to create the database and tables
            try:
                vessel_query = f"SELECT * FROM vessel_history WHERE sfon_no = {sfon} ORDER BY CAST(rev AS SIGNED) DESC LIMIT 1;"
                cursor.execute(vessel_query)
                # Fetch all results
                rows = cursor.fetchall()
                vessel_details = None
                if len(rows) > 0:
                    vessel_details = rows[0]
                    reactor_query = f"select name from master_model where id={vessel_details['model_id']};"
                    cursor.execute(reactor_query)
                    reactor = cursor.fetchall()
                    vessel_details['reactor'] = reactor[0]['name']

                    model_query = f"select name from master_capacity where id={vessel_details['reactor_id']};"
                    cursor.execute(model_query)
                    model = cursor.fetchall()
                    vessel_details['model'] = model[0]['name']

                    glass_query = f"select name from master_glass where id={vessel_details['glass_id']};"
                    cursor.execute(glass_query)
                    glass = cursor.fetchall()
                    vessel_details['glass'] = glass[0]['name']

                    ndt_query = f"select name from master_ndt where id={vessel_details['ndt']};"
                    cursor.execute(ndt_query)
                    ndt = cursor.fetchall()
                    vessel_details['ndt_value'] = ndt[0]['name']

                    design_temperature_query = f"select name from master_temperature where id={vessel_details['temperature']};"
                    cursor.execute(design_temperature_query)
                    design_temperature = cursor.fetchall()
                    vessel_details['design_temperature'] = design_temperature[0]['name']

                    design_pressure_query = f"select name from master_pressure where id={vessel_details['pressure']};"
                    cursor.execute(design_pressure_query)
                    design_pressure = cursor.fetchall()
                    vessel_details['design_pressure'] = design_pressure[0]['name']

                    agitator_types_list = json.loads(vessel_details['agitator_type'])

                    agitator_types = []
                    for type in agitator_types_list:
                        if type != None:
                            type_query = f"SELECT name from master_agitator_type WHERE id='{type}'"
                            cursor.execute(type_query)
                            fetched_type = cursor.fetchall()
                            agitator_types.append(fetched_type[0]['name'])
                    vessel_details['agitator_flight_types'] = agitator_types

                    sealing_type_query = f"SELECT * from master_drive_shaft_type where id='{vessel_details['agitator_d_shaft_type']}';"
                    cursor.execute(sealing_type_query)
                    sealing_type = cursor.fetchall()
                    vessel_details['sealing_type'] = sealing_type[0]['name']

                    jacket_type_query = f"SELECT name from master_jacket_type where id={vessel_details['jacket_type']};"
                    cursor.execute(jacket_type_query)
                    jacket_type = cursor.fetchall()
                    vessel_details['jacketType'] = jacket_type[0]['name']

                    jacket_pressure_query = f"SELECT name from master_pressure where id={vessel_details['jacket_pressure']};"
                    cursor.execute(jacket_pressure_query)
                    jacket_pressure = cursor.fetchall()
                    vessel_details['jacketPressure'] = jacket_pressure[0]['name']

                    jacket_support_query = f"SELECT name from master_support where id={vessel_details['jacket_support']};"
                    cursor.execute(jacket_support_query)
                    jacket_support = cursor.fetchall()
                    vessel_details['jacketSupport'] = jacket_support[0]['name']

                    jacket_temperature_query = f"SELECT name from master_temperature where id={vessel_details['jacket_temperature']};"
                    cursor.execute(jacket_temperature_query)
                    jacket_temperature = cursor.fetchall()
                    vessel_details['jacketTemperature'] = jacket_temperature[0]['name']

                    jacket_ndt_query = f"SELECT name from master_jacket_ndt where id={vessel_details['jacket_ndt']};"
                    cursor.execute(jacket_ndt_query)
                    jacket_ndt = cursor.fetchall()
                    vessel_details['jacketNDT'] = jacket_ndt[0]['name']

                    jacket_material_query = f"SELECT name from master_material_shell_jacket where id={vessel_details['jacket_material_shell']};"
                    cursor.execute(jacket_material_query)
                    jacket_material = cursor.fetchall()
                    vessel_details['jacketMaterialShell'] = jacket_material[0]['name']

                    nozzle_material_query = f"SELECT name from master_material_nozzle_jacket where id={vessel_details['jacket_material_nozzle']};"
                    cursor.execute(nozzle_material_query)
                    nozzle_material = cursor.fetchall()
                    vessel_details['jacketMaterialNozzle'] = nozzle_material[0]['name']

                    jacket_material_earting_type_query = f"SELECT name from master_material_earthing where id={vessel_details['material_earthing']};"
                    cursor.execute(jacket_material_earting_type_query)
                    material_earthing_type = cursor.fetchall()
                    vessel_details['material_earthing_type'] = material_earthing_type[0]['name']

                    shaft_type_query = f"SELECT name from master_drive_shaft_type where id={vessel_details['agitator_d_shaft_type']};"
                    cursor.execute(shaft_type_query)
                    shaft_type = cursor.fetchall()
                    vessel_details['shaft_type'] = shaft_type[0]['name']                    

                    shaft_make_query = f"SELECT name from master_drive_shaft_make where id={vessel_details['agitator_d_shaft_make']};"
                    cursor.execute(shaft_make_query)
                    shaft_make = cursor.fetchall()
                    vessel_details['shaft_make'] = shaft_make[0]['name']

                    shaft_housing_query = f"SELECT name from master_drive_shaft_housing where id={vessel_details['agitator_d_shaft_house']};"
                    cursor.execute(shaft_housing_query)
                    shaft_housing = cursor.fetchall()
                    vessel_details['shaft_housing'] = shaft_housing[0]['name']

                    shaft_sealing_query = f"SELECT name from master_drive_shaft_sealing where id={vessel_details['agitator_d_shaft_seal']};"
                    cursor.execute(shaft_sealing_query)
                    shaft_sealing = cursor.fetchall()
                    vessel_details['shaft_sealing'] = shaft_sealing[0]['name']

                    shaft_inboard_query = f"SELECT name from master_drive_shaft_inborad where id={vessel_details['agitator_d_shaft_in']};"
                    cursor.execute(shaft_inboard_query)
                    shaft_inboard = cursor.fetchall()
                    vessel_details['shaft_inboard'] = shaft_inboard[0]['name']

                    if vessel_details['agitator_d_shaft_out'] != None:
                        shaft_outboard_query = f"SELECT name from master_drive_shaft_outborad where id={vessel_details['agitator_d_shaft_out']};"
                        cursor.execute(shaft_outboard_query)
                        shaft_outboard = cursor.fetchall()
                        vessel_details['shaft_outboard'] = shaft_outboard[0]['name']
                    else:
                        vessel_details['shaft_outboard'] = None
                    
                    if vessel_details['agitator_d_shaft_other'] != None:
                        shaft_other_query = f"SELECT name from master_drive_shaft_outborad where id={vessel_details['agitator_d_shaft_other']};"
                        cursor.execute(shaft_other_query)
                        shaft_other = cursor.fetchall()
                        vessel_details['shaft_other'] = shaft_other[0]['name']
                    else:
                        vessel_details['shaft_other'] = None

                    # agitator_d_gear_make
                    gear_make_query = f"SELECT name from master_drive_gear_make where id={vessel_details['agitator_d_gear_make']};"
                    cursor.execute(gear_make_query)
                    gear_make = cursor.fetchall()
                    vessel_details['gear_make'] = gear_make[0]['name']

                    # agitator_d_gear_type
                    gear_type_query = f"SELECT name from master_drive_gear_type where id={vessel_details['agitator_d_gear_type']};"
                    cursor.execute(gear_type_query)
                    gear_type = cursor.fetchall()
                    vessel_details['gear_type'] = gear_type[0]['name']

                    # agitator_d_motor_make
                    motor_make_query = f"SELECT name from master_drive_motor_make where id={vessel_details['agitator_d_motor_make']};"
                    cursor.execute(motor_make_query)
                    motor_make = cursor.fetchall()
                    vessel_details['motor_make'] = motor_make[0]['name']

                    # agitator_d_motor_mounting
                    motor_mounting_query = f"SELECT name from master_drive_motor_mounting where id={vessel_details['agitator_d_motor_mounting']};"
                    cursor.execute(motor_mounting_query)
                    motor_mounting = cursor.fetchall()
                    vessel_details['motor_mounting'] = motor_mounting[0]['name']

                    # agitator_d_motor_type_1
                    motor_standard_query = f"SELECT name from master_drive_motor_type_1 where id={vessel_details['agitator_d_motor_type_1']};"
                    cursor.execute(motor_standard_query)
                    motor_standard = cursor.fetchall()
                    vessel_details['motor_standard'] = motor_standard[0]['name']

                    # agitator_d_motor_type_2
                    motor_type_query = f"SELECT name from master_drive_motor_type_2 where id={vessel_details['agitator_d_motor_type_2']};"
                    cursor.execute(motor_type_query)
                    motor_type = cursor.fetchall()
                    vessel_details['motor_type'] = motor_type[0]['name']

                    # v_agitator_d_motor_hp
                    motor_hp_query = f"SELECT name from master_drive_hp where id={vessel_details['v_agitator_d_motor_hp']};"
                    cursor.execute(motor_hp_query)
                    motor_hp = cursor.fetchall()
                    vessel_details['motor_hp'] = motor_hp[0]['name']

                    # master_material_gasket -> material_gasket
                    master_material_gasket_query = f"SELECT name from master_material_gasket where id={vessel_details['material_gasket']};"
                    cursor.execute(master_material_gasket_query)
                    gasket = cursor.fetchall()
                    vessel_details['gasket'] = gasket[0]['name']

                    # master_material_fasteners_pressure -> material_fasteners
                    master_material_fasteners_pressure_query = f"SELECT name from master_material_fasteners_pressure where id={vessel_details['material_fasteners']};"
                    cursor.execute(master_material_fasteners_pressure_query)
                    fastener = cursor.fetchall()
                    vessel_details['fastener'] = fastener[0]['name']

                    # master_material_split -> material_split
                    master_material_split_query = f"SELECT name from master_material_split where id={vessel_details['material_split']};"
                    cursor.execute(master_material_split_query)
                    split_flange = cursor.fetchall()
                    vessel_details['split_flange'] = split_flange[0]['name']

                    print(f"Successfully fetched.")
                
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
            cursor.execute(f"USE ofn")
            try:
                model_info = data['model_info']
                model_id = model_info['modelId']
                reactor_id = model_info['reactorId']

                capacity_id_query = f"SELECT id FROM master_capacity WHERE capacity='{model_info['capacity']}' AND name='{model_info['model']}';"
                cursor.execute(capacity_id_query)
                rows = cursor.fetchall()
                capacity_id = rows[0]['id']

                masters = list(data['masters'].keys())
                for master in masters:
                    if master == 'component':
                        continue
                    if master == 'master_jacket_type':
                        master_jacket_type_query = f"SELECT name FROM master_jacket_type WHERE capacity_id='{capacity_id}' and status='1';"
                        cursor.execute(master_jacket_type_query)
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_temperature':
                        master_temperature_query = f"SELECT name FROM master_temperature WHERE model_id='{reactor_id}';"
                        cursor.execute(master_temperature_query)
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_pressure':
                        master_pressure_query = f"SELECT name FROM master_pressure WHERE model_id='1';"
                        cursor.execute(master_pressure_query)
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_jacket_ndt':
                        master_jacket_ndt_query = f"SELECT name FROM master_jacket_ndt WHERE capacity_id='1';"
                        cursor.execute(master_jacket_ndt_query)
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_drive_hp':
                        master_drive_hp_query = f"SELECT name FROM master_drive_hp WHERE capacity_id={capacity_id};"
                        cursor.execute(master_drive_hp_query)
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_material_gasket':
                        master_material_gasket_query = f"SELECT name FROM master_material_gasket WHERE status='1';"
                        cursor.execute(master_material_gasket_query)
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_material_fasteners_pressure':
                        master_material_fasteners_pressure_query = f"SELECT name FROM master_material_fasteners_pressure WHERE status='1';"
                        cursor.execute(master_material_fasteners_pressure_query)
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    elif master == 'master_material_split':
                        master_material_split_query = f"SELECT name FROM master_material_split WHERE status='1';"
                        cursor.execute(master_material_split_query)
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                    else:
                        vessel_query = f"SELECT name FROM {master};"
                        cursor.execute(vessel_query)
                        rows = cursor.fetchall()
                        data['masters'][master] = rows
                return data
            except mysql.connector.Error as err:
                print(f"Error: {err}")
            finally:
                cursor.close()
        except Exception as e:
            print(f"Error while fetching data from table: {e}")
