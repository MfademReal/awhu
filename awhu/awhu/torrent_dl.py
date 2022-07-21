import libtorrent as lt
import time
import logging
import sys
import os
def torrent_downloader(magnet_link:str,download_all:bool=False,torrent_filename:str=""):
    ses = lt.session()
    ses.listen_on(6881, 6891)
    params = {
        'save_path': '.',
        'storage_mode': lt.storage_mode_t(2)}
    handle = lt.add_magnet_uri(ses, magnet_link, params)
    ses.start_dht()

    begin = time.time()

    logging.warning('Downloading Metadata...')
    while (not handle.has_metadata()):
        time.sleep(1)
    logging.warning('Got Metadata, Starting Torrent Download...')
    info = handle.get_torrent_info()
    if(not download_all):
        pr = [0 for i in range(sum(1 for _ in info.files()))]
        found = False
        file_dl=None
        for i, f in enumerate(info.files()):
            if(torrent_filename in f.path.split("/")[-1].strip()):
                pr[i] = 4
                file_dl=f
                found = True
                break
        if(not found):
            logging.warning("فایل مورد نظر پیدا نشد")
            exit
        handle.prioritize_files(pr)
        toks=file_dl.path.split("/")
        file_dl_name=toks[-1]
    else: file_dl_name=handle.name()
    
    logging.warning(f"Starting {file_dl_name}")

    while (handle.status().state != lt.torrent_status.seeding):
        s = handle.status()
        state_str = ['queued', 'checking', 'downloading metadata',
                     'downloading', 'finished', 'seeding', 'allocating']
        sys.stdout.write('\r')
        sys.stdout.write('%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s ' %
                         (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
                          s.num_peers, state_str[s.state]))
        sys.stdout.flush()
        if(s.progress == 1):
            break
        time.sleep(5)

    if(handle.name()!=file_dl_name):
        os.system(f"mv \"{file_dl.path}\" .")
        os.system(f"rm -r \"{handle.name()}\"")
    end = time.time()
    logging.warning(f"\n{file_dl_name} COMPLETE")
    logging.warning(f"Elapsed Time: {int((end-begin)//60)}min: {int((end-begin) % 60)}sec")
    return file_dl_name