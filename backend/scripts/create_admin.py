import getpass
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..'))
from app.main import db, pwd
from sqlalchemy import text

email = input('Correo del administrador [admin@cineia.local]: ').strip().lower() or 'admin@cineia.local'
full_name = input('Nombre completo [Administrador CineIA]: ').strip() or 'Administrador CineIA'
password = getpass.getpass('Contraseña (mínimo 8 caracteres): ')
confirmation = getpass.getpass('Confirma la contraseña: ')
if len(password) < 8:
 raise SystemExit('La contraseña debe tener al menos 8 caracteres.')
if password != confirmation:
 raise SystemExit('Las contraseñas no coinciden.')

with db() as c:
 existing = c.execute(text('SELECT id FROM app_users WHERE email=:e'), {'e': email}).first()
 if existing:
  raise SystemExit('Ya existe un usuario con ese correo.')
 c.execute(
  text("INSERT INTO app_users(email,full_name,password_hash,role) VALUES(:e,:n,:p,'ADMIN')"),
  {'e': email, 'n': full_name, 'p': pwd.hash(password)},
 )
 c.commit()
print('Administrador creado correctamente:', email)
