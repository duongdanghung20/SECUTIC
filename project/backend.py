#!/usr/bin/python3
import subprocess
import os
import requests
import qrcode
import hashlib
import zbarlight
from PIL import Image
from steganography import cacher, recuperer

INFO_BLOCK_LEN = 64
QRCODE_SIZE = 210

def pad(info):
    """
    This function is used to pad the information block to fill a 64-byte string
    - Input: the information block (name||certificate_title)
    - Output: the byte string of length 64, with the information block padded
    """

    # Calculate the number of bytes to be padded
    padding_len = INFO_BLOCK_LEN - len(info) 

    # Pad the string with the byte whose value = (number_of_pading_bytes - 1)
    return info.encode() + padding_len * int.to_bytes(padding_len - 1, 1, 'big')

def sign(info_fname):
    """
    This function takes a filename as input, sign the file and return the signature which was converted to ASCII format
    - Input: filename of the file containing the information block
    - Output: the signature signed by the private key of the server, converted to ASCII format
    """
    # Name of the file which will contain the signature
    sig_fname = info_fname + ".sig"

    # Sign the information block with private key
    sign_cmd = ['openssl',
                'dgst',
                '-sha256',
                '-sign',
                './ecc/ecc.serveur.key.pem',
                '-out',
                sig_fname,
                info_fname]
    subprocess.run(sign_cmd)

    # Get the signature
    with open(sig_fname, 'rb') as f:
        signature = f.read()
        signature_ascii = signature.hex()
    os.remove(sig_fname)

    return signature_ascii

def extract_signature(fname):
    """
    This function extract the signature from the QR code of a certificate
    - Input: filename of the certificate
    - Output: the signature extracted from the QR code, converted to bytes
    """

    # Crop the QR code region from the image
    attestation = Image.open(fname)
    qrImage = attestation.crop((1418,934,1418+QRCODE_SIZE,934+QRCODE_SIZE))
    signature_ascii = zbarlight.scan_codes(['qrcode'], qrImage)[0].decode()

    # Convert the signature from ASCII format to byte string format
    signature = bytes.fromhex(signature_ascii)
    return signature

def timestamp(info_fname):
    """
    This function takes a filename as input, send a TimeStampRequest for this file to freeTSA.org, then return the TimeStampResponse received
    - Input: filename of the file containing the information block
    - Output: the TimeStampResponse (in bytes) returned from freeTSA.org
    """
    tsq_fname = info_fname + ".tsq"  # Name of the file containing the TimeStampRequest

    # Create a TimeStampRequest 
    tsr_cmd = ['openssl',
                'ts',
                '-query',
                '-data',
                info_fname,
                '-no_nonce',
                '-sha256',
                '-cert',
                '-out',
                tsq_fname]
    subprocess.run(tsr_cmd)

    # Send the TimeStampRequest to freeTSA.org and receive a TimeStampResponse file 
    url = 'https://freetsa.org/tsr'
    headers = {'Content-Type': 'application/timestamp-query'}
    with open(tsq_fname, 'rb') as f:
        tsq_data = f.read()

    response = requests.post(url, headers=headers, data=tsq_data)

    os.remove(tsq_fname)

    return response.content

def add_stegano(info_fname, timestamp_data, cert_fname, stegano_fname):
    """
    This function dissimulate the information block and the timestamp to the certificate
    - Input:
        + info_fname: the filename of the file containing the information block (name||certificate_title)
        + timestamp_data: the TimeStampResponse (in bytes)
        + cert_fname: the name of the certificate image without steganography
        + stegano_fname: the name of the certificate image after steganography
    """
    
    with open(info_fname, "rb") as f:
        info_data = f.read()
    # Convert (info||timestamp) to ASCII format and dissimulate it into the image using steganography
    stegano_data = (info_data + timestamp_data).hex()

    # Add stegano data to the image
    img_fname = cert_fname
    stegano_img_fname = stegano_fname
    img = Image.open(img_fname)
    cacher(img, stegano_data)
    img.save(stegano_img_fname)
    img.close()

def extract_stegano(stegano_fname, timestamp_algo="sha256"):
    """
    This function extract the hidden steganography data in the image
    - Input: the filename of the certificate image (which was likely to be dissimulated with steganography)
    - Output: the hidden steganography data
    """
    if timestamp_algo == "sha256":
        len_timestamp_data = 5462 + INFO_BLOCK_LEN  # Constant 5462 bytes, as tested with freeTSA.org
    len_stegano_data = 2 * len_timestamp_data       # x2 since we convert bytes to hexadecimal string to dissimulate
    img = Image.open(stegano_fname)
    retrieved_msg = recuperer(img, len_stegano_data)
    img.close()
    return bytes.fromhex(retrieved_msg)

def render_cert(identity, cert_title, src_ip_address_hash):
    """
    This function renders the certificate, given a specific identity (name), the title of the certificate, and the source IP address (hashed) who make the request
    - Input:
        + identity: the given name
        + cert_title: the given title of the certificate
        + src_ip_address_hash: the source IP address (hashed with SHA-256)
    """
    info = identity + cert_title
    info_fname = src_ip_address_hash  # Name of the file containing the information block
    with open(info_fname, 'wb') as f:
        f.write(pad(info))

    # Define necessary file names
    bg_fname = "./imgs/cert_bg.png"
    text_fname = f'./imgs/{info_fname}_text.png'
    qr_fname = f'./imgs/{info_fname}_qr.png'
    text_bg_fname = f'./imgs/{info_fname}_text_bg.png'
    text_bg_qr_fname = f'./imgs/{info_fname}_text_bg_qr.png'
    final_fname = f'./imgs/{info_fname}_final.png'
    temp_fnames = [text_fname, qr_fname, text_bg_fname, text_bg_qr_fname]

    
    # Render the Identity and Certificate Title text lines image
    text_line = f"Certificat {cert_title}|délivré à|{identity}"
    curl_cmd = [
        "curl",
        "-o",
        text_fname,
        "http://chart.apis.google.com/chart",
        "--data-urlencode",
        "chst=d_text_outline",
        "--data-urlencode",
        f"chld=000000|56|h|FFFFFF|b|{text_line}"
    ]
    subprocess.run(curl_cmd)

    # Resize the text lines
    resize_txt_cmd = ['mogrify', '-resize', '800x480', text_fname]
    subprocess.run(resize_txt_cmd)

    # Sign the certificate and put the signature in the QR code
    signature = sign(info_fname)

    qr = qrcode.make(signature)
    qr.save(qr_fname, scale=2)

    resize_qrcode_cmd = ['mogrify', '-resize', f'{QRCODE_SIZE}x{QRCODE_SIZE}', qr_fname]
    subprocess.run(resize_qrcode_cmd)

    # Intergrate the text lines to the image background
    render_cert_cmd = ['composite',
                        '-gravity',
                        'center',
                        text_fname,
                        bg_fname,
                        text_bg_fname]
    subprocess.run(render_cert_cmd)

    # Integrate the QR code to the cert
    add_qr_cmd = ['composite',
                '-geometry',
                '+1418+934',
                qr_fname,
                text_bg_fname,
                text_bg_qr_fname]
    subprocess.run(add_qr_cmd)

    # Request the timestamp from freeTSA.org
    timestamp_data = timestamp(info_fname)

    # Dissimulation of information to the cert by steganography
    add_stegano(info_fname=info_fname, timestamp_data=timestamp_data, cert_fname=text_bg_qr_fname, stegano_fname=final_fname)

    # Remove temporary files
    for fname in temp_fnames:
        os.remove(fname)
    os.remove(info_fname)

def verify_cert(src_ip_address_hash):
    """
    This function verifies the certificate provided by a client
    - Input: The source IP address (hashed with SHA-256) who requests his certificate to be verified 
    """
    verify_fname = f'./imgs/{src_ip_address_hash}_verify.png'

    # Try to retrieve stegano data from the image (if no stegano data dissimulated then verification failed)
    try:
        stegano_data = extract_stegano(verify_fname)
        info_block_data = stegano_data[:INFO_BLOCK_LEN]
        time_stamp_data = stegano_data[INFO_BLOCK_LEN:]
    except Exception:
        os.remove(verify_fname)
        return False

    info_block_fname = f"{src_ip_address_hash}_info_block"
    time_stamp_fname = f"{src_ip_address_hash}_time_stamp"
    with open(info_block_fname, "wb") as f:
        f.write(info_block_data)
    with open(time_stamp_fname, "wb") as f:
        f.write(time_stamp_data)
    
    # Verify the timestamp dissimulated in the image by steganography
    verify_timestamp_cmd = ['openssl',
                'ts',
                '-verify',
                '-data',
                info_block_fname,
                '-in',
                time_stamp_fname,
                '-CAfile',
                './tsp/cacert.pem',
                '-untrusted',
                './tsp/tsa.crt']

    verify_timestamp_result = subprocess.run(verify_timestamp_cmd, capture_output=True).stdout.decode()

    os.remove(time_stamp_fname)

    if "OK" not in verify_timestamp_result:
        return False
    
    # Retrieve stegano data from the image (if no stegano data dissimulated then verification failed)
    signature = extract_signature(verify_fname)
    signature_fname = f'{src_ip_address_hash}.sig'
    with open(signature_fname, "wb") as f:
        f.write(signature)

    # Verify the signature in the image using the public key
    verify_signature_cmd = ['openssl',
                            'dgst',
                            '-sha256',
                            '-verify',
                            './ecc/ecc.serveur.pubkey.pem',
                            '-signature',
                            signature_fname,
                            info_block_fname]
    
    verify_signature_result = subprocess.run(verify_signature_cmd, capture_output=True).stdout.decode()

    # Remove redundant files
    os.remove(verify_fname)
    os.remove(info_block_fname)
    os.remove(signature_fname)

    if "OK" not in verify_signature_result:
        return False
    
    return True
    
    
