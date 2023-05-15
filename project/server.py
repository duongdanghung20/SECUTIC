#!/usr/bin/python3

from bottle import route, run, template, request, response
from backend import render_cert, verify_cert
import hashlib

@route('/creation', method='POST')
def creation():
    contenu_identite = request.params['identite']
    contenu_intitule_certification = request.params['intitule_certif']
    
    print('nom prénom :', contenu_identite, ' intitulé de la certification :', contenu_intitule_certification)

    # ================================ Add code to render the certification ======================================

    # Get the source IP address
    src_ip_address = request.environ.get('REMOTE_ADDR')

    # Hash the source IP address with SHA-256
    src_ip_address_hash = hashlib.sha256(bytes(src_ip_address, "utf-8")).hexdigest()

    # Render the certificate for the IP address requested
    render_cert(identity=contenu_identite, cert_title=contenu_intitule_certification, src_ip_address_hash=src_ip_address_hash)

    # ============================================================================================================
    
    response.set_header('Content-type', 'text/plain')
    return 'ok!\r\n'

@route('/verification', method='POST')
def verification():
    contenu_image = request.files.get('image')

    # ================================ Add code to render the certification ======================================

    # Get the source IP address
    src_ip_address = request.environ.get('REMOTE_ADDR')

    # Hash the source IP address with SHA-256
    src_ip_address_hash = hashlib.sha256(bytes(src_ip_address, "utf-8")).hexdigest()

    # Save the image submitted by the client
    contenu_image.save(f'./imgs/{src_ip_address_hash}_verify.png', overwrite=True)
    
    response.set_header('Content-type', 'text/plain')

    # Return the verification result
    if verify_cert(src_ip_address_hash):
        return 'Certified!\r\n'
    return 'Erroneous Certificate!\r\n'

@route('/fond')
def fond():

    # ================================ Add code to return the certification ======================================
    
    # Get the source IP address
    src_ip_address = request.environ.get('REMOTE_ADDR')

    # Hash the source IP address with SHA-256
    src_ip_address_hash = hashlib.sha256(bytes(src_ip_address, "utf-8")).hexdigest()

    response.set_header('Content-type', 'image/png')

    # Return the certification requested to the client who requests it
    try:
        with open(f'./imgs/{src_ip_address_hash}_final.png','rb') as descripteur_fichier:
            contenu_fichier = descripteur_fichier.read()
    except Exception:
        return "You have not submit your information yet"

    # Here I don't remove the image file after sending it to the client
    # because the client can request it again?

    # ============================================================================================================

    return contenu_fichier

# start server
run(host='0.0.0.0', port=8080, debug=True)