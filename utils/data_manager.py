# import asyncpg

async def get_all_members_details(pool):
    query="""
        SELECT m.id, m.name, m.role, r.responsibility_text
        FROM members m
        LEFT JOIN responsibilities r ON m.id = r.member_id;        
        """
    records = await pool.fetch(query)

    members_dict= {}

    for record in records:
        member_id = record['id']
        if member_id not in members_dict:
            members_dict[member_id] = {
                "name": record['name'],
                "role": record['role'],
                "responsibilities": []
            }
        if record['responsibility_text']:
            members_dict[member_id]['responsibilities'].append(record['responsibility_text'])
    return list(members_dict.values())

async def get_simple_member_list(pool):
    query = "SELECT name, role FROM members ORDER BY name;"
    try:
        records = await pool.fetch(query)
        return records
    except Exception as e:
        print(f"Error fetching members from DB: {e}")
        return []

async def add_member_to_db(pool, name: str, role: str):
    query = "INSERT INTO members (name, role) VALUES ($1, $2);"
    try:
        await pool.execute(query, name, role)
        return True
    except Exception as e:
        print(f"Error adding member to DB: {e}")
        return False
    


async def delete_member_from_db(pool, name: str):
    query = "DELETE FROM members WHERE lower(name) = lower($1) RETURNING name;"
    try:
        deleted_member_name = await pool.fetchval(query, name)
        return deleted_member_name
    except Exception as e:
        print(f"Error deleting member from DB: {e}")
        return None
    

async def edit_member_in_db(pool, current_name: str, new_name: str = None, new_role: str = None):
    #Updates a member's name and/or role in the database.
    if new_name is None and new_role is None:
        return None # Nothing to update

    updates = []
    params = []
    param_count = 1

    if new_name is not None:
        updates.append(f"name = ${param_count}")
        params.append(new_name)
        param_count += 1
    
    if new_role is not None:
        updates.append(f"role = ${param_count}")
        params.append(new_role)
        param_count += 1


    params.append(current_name)
    
    update_string = ", ".join(updates)
    
    query = f"UPDATE members SET {update_string} WHERE lower(name) = lower(${param_count}) RETURNING name;"

    try:
        updated_member_name = await pool.fetchval(query, *params)
        return updated_member_name
    except Exception as e:
        print(f"Error editing member in DB: {e}")
        return None

    
async def add_responsibility_to_db(pool, member_name: str, responsibility_text:str):
    try:
        member_id_query = "SELECT id FROM members WHERE lower(name) = lower($1);"
        member_id = await pool.fetchval(member_id_query, member_name)

        if member_id is None:
            return "member_not_found"
        
        insert_query = "INSERT INTO responsibilities (member_id, responsibility_text) VALUES ($1, $2);"
        await pool.execute(insert_query, member_id, responsibility_text)
        return "success"
    except Exception as e:
        print(f"Error adding responsibility to DB: {e}")
        return "error"



async def get_all_rules_from_db(pool):
    query = "SELECT id, rule_text FROM rules ORDER BY id;"
    try:
        return await pool.fetch(query)
    except Exception as e:
        print(f"Error fetching rules from DB: {e}")
        return []

async def add_rule_to_db(pool, rule_text: str):
    query = "INSERT INTO rules (rule_text) VALUES ($1);"
    try:
        await pool.execute(query, rule_text)
        return True
    except Exception as e:
        print(f"Error adding rule to DB: {e}")
        return False

async def delete_rule_from_db(pool, rule_id: int):
    query = "DELETE FROM rules WHERE id = $1 RETURNING rule_text;"
    try:
        return await pool.fetchval(query, rule_id)
    except Exception as e:
        print(f"Error deleting rule from DB: {e}")
        return None

async def get_member_id_by_name(pool, name: str):
    
    query = "SELECT id FROM members WHERE lower(name) = lower($1);"
    return await pool.fetchval(query, name)

async def add_task_to_db(pool, member_id: int, description: str):
    
    query = "INSERT INTO tasks (member_id, task_description, status) VALUES ($1, $2, 'pending') RETURNING id;"
    try:
        new_task_id = await pool.fetchval(query, member_id, description)
        return new_task_id
    except Exception as e:
        print(f"Error adding task to DB: {e}")
        return None

async def get_tasks_from_db(pool, member_name: str = None):
    
    if member_name:
        query = """
            SELECT t.id, t.task_description, m.name as assigned_to
            FROM tasks t
            JOIN members m ON t.member_id = m.id
            WHERE t.status = 'pending' AND lower(m.name) = lower($1)
            ORDER BY t.id;
        """
        return await pool.fetch(query, member_name)
    else:
        query = """
            SELECT t.id, t.task_description, m.name as assigned_to
            FROM tasks t
            JOIN members m ON t.member_id = m.id
            WHERE t.status = 'pending'
            ORDER BY t.id;
        """
        return await pool.fetch(query)

async def update_task_status_in_db(pool, task_id: int, status: str):
    
    query = "UPDATE tasks SET status = $1 WHERE id = $2 RETURNING id;"
    try:
        return await pool.fetchval(query, status, task_id)
    except Exception as e:
        print(f"Error updating task status: {e}")
        return None


async def get_full_member_details(pool, name:str):
    query = """
    SELECT 
        m.name, m.role,
        r.id as responsibility_id, r.responsibility_text,
        t.id as task_id, t.task_description
    FROM members m
    LEFT JOIN responsibilities r ON m.id = r.member_id
    LEFT JOIN tasks t ON m.id = t.member_id AND t.status = 'pending'
    WHERE lower(m.name) = lower($1);
    """
    records = await pool.fetch(query, name)
    
    if not records:
        return None

    # Process the database records into a single dictionary
    member_details = {
        "name": records[0]['name'],
        "role": records[0]['role'],
        "responsibilities": list(set((r['responsibility_id'], r['responsibility_text']) for r in records if r['responsibility_id'])),
        "tasks": list(set((r['task_id'], r['task_description']) for r in records if r['task_id']))
    }
    member_details['responsibilities'].sort()
    member_details['tasks'].sort()
    
    return member_details


async def delete_responsibility_from_db(pool, responsibility_id: int):
    query = "DELETE FROM responsibilities WHERE id = $1 RETURNING responsibility_text;"
    try:
        return await pool.fetchval(query, responsibility_id)
    except Exception as e:
        print(f"Error deleting responsibility from DB: {e}")
        return None
    
async def get_all_responsibilities_with_member(pool):
    query = """
        SELECT r.id, r.responsibility_text, m.name as member_name
        FROM responsibilities r
        JOIN members m ON r.member_id = m.id
        ORDER BY m.name, r.id;
    """
    try:
        return await pool.fetch(query)
    except Exception as e:
        print(f"Error fetching responsibilities from DB: {e}")
        return []