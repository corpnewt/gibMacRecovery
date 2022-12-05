#!/usr/bin/env python
from Scripts import downloader,utils,run
import os, shutil, sys, json

class gibMacRecovery:
    def __init__(self):
        self.d = downloader.Downloader()
        self.u = utils.Utils("gibMacRecovery")
        self.r = run.Run()
        if sys.version_info < (3, 0):
            maj,mnr,mic = sys.version_info[:3]
            self.u.head()
            print("")
            print("Incompatible python version!")
            print("macrecovery.py requires at least python 3")
            print("")
            print("Currently running {}.{}.{}".format(maj,mnr,mic))
            print("")
            self.u.grab("Press [enter] to exit...")
            exit()
        self.boards_url = "https://raw.githubusercontent.com/acidanthera/OpenCorePkg/master/Utilities/macrecovery/boards.json"
        self.boards_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Scripts",os.path.basename(self.boards_url))
        self.macrecovery_url = "https://raw.githubusercontent.com/acidanthera/OpenCorePkg/master/Utilities/macrecovery/macrecovery.py"
        self.macrecovery_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Scripts",os.path.basename(self.macrecovery_url))
        self.recovery_url = "https://github.com/acidanthera/OpenCorePkg/raw/master/Utilities/macrecovery/recovery_urls.txt"
        self.recovery_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Scripts",os.path.basename(self.recovery_url))
        self.output = os.path.join(os.path.dirname(os.path.realpath(__file__)),"com.apple.recovery.boot")
        self.min_w = 80
        self.min_h = 24
        if os.name == "nt":
            self.min_w = 120
            self.min_h = 30
        self.resize()
        if not os.path.exists(self.boards_path) or not os.path.exists(self.macrecovery_path) or not os.path.exists(self.recovery_path):
            self.update_macrecovery()
        self.boards = {}
        if os.path.exists(self.boards_path):
            try: self.boards = json.load(open(self.boards_path))
            except: pass
        self.recovery = self.parse_recovery()
        self.target_macos = None
        self.target_mac = None
        self.target_mlb = None
        self.latest_default = "default"

    def update_macrecovery(self):
        self.u.head("Downloading Required Files")
        print("")
        try:
            for path,url in ((self.boards_path,self.boards_url),(self.macrecovery_path,self.macrecovery_url),(self.recovery_path,self.recovery_url)):
                print("Downloading {}...".format(os.path.basename(path)))
                self.d.stream_to_file(url,path,False)
        except Exception as e:
            print("Something went wrong:\n{}\n".format(e))
            self.u.grab("Press [enter] to return...")
            return
        print("\nDone.\n")
        self.u.grab("Returning in 5 seconds...",timeout=5)

    def parse_recovery(self):
        if not os.path.exists(self.recovery_path):
            return {}
        with open(self.recovery_path,"r") as f:
            r = f.read()
        r_dict = {}
        last_os = None
        for line in r.split("\n"):
            if not line.strip(): continue # Skip empty lines
            if line.lower().startswith(("diagnostics","default")):
                last_os = None
                continue
            if line.startswith("./") and last_os and not "<" in line:
                # Got some info - let's get the 3rd and 5th elements
                try:
                    parts = line.split()
                    comm_list = r_dict.get(last_os,[])
                    comm_list.append({
                        "board_id":parts[2],
                        "mlb":parts[4]
                    })
                    r_dict[last_os] = comm_list
                except:
                    continue
            elif not line.startswith("./"):
                last_os = line.strip().rstrip(":").replace(" version","")
        return r_dict            

    def resize(self, width=0, height=0):
        self.u.resize(max(width,self.min_w),max(height,self.min_h))

    def select_target_macos(self):
        os_list = sorted(list(set(self.boards.values())),reverse=True)
        while True:
            self.u.head("Select Target macOS Version")
            print("")
            print("     Target macOS: {}".format(self.target_macos))
            print("  Target Board ID: {}".format(self.target_mac))
            print("       Target MLB: {}".format(self.target_mlb))
            print("")
            if not self.boards:
                print("No macOS versions found!  Make sure boards.json is in the Scripts directory,")
                print("and is a valid json file!")
                print("")
                self.u.grab("Press [enter] to return...")
                return (self.target_macos,self.target_mac,self.target_mlb,self.latest_default)
            for i,v in enumerate(os_list,start=1):
                print("{}. {}".format(str(i),v))
            print("")
            print("M. Main Menu")
            print("Q. Quit")
            print("")
            menu = self.u.grab("Please select an option:  ")
            if not menu: continue
            if menu.lower() == "m": return (self.target_macos,self.target_mac,self.target_mlb,self.latest_default)
            elif menu.lower() == "q": self.u.custom_quit()
            try:
                menu = int(menu)-1
                assert 0 <= menu < len(os_list)
            except:
                continue
            # We have a valid menu item - let's get the OS version, and the first
            # mac model
            for mac in self.boards:
                if self.boards[mac].lower() == os_list[menu]:
                    # Got it
                    return (os_list[menu],mac,"00000000000000000","latest" if "latest" in os_list[menu].lower() else "default")

    def input_mac_model(self):
        while True:
            self.u.head("Input Custom Board ID")
            print("")
            print("     Target macOS: {}".format(self.target_macos))
            print("  Target Board ID: {}".format(self.target_mac))
            print("       Target MLB: {}".format(self.target_mlb))
            print("   Latest/Default: {}".format(self.latest_default))
            print("")
            print("Board IDs must begin with 'Mac-' followed by 8 or 16 hexadecimal digits.")
            print("")
            print("M. Main Menu")
            print("Q. Quit")
            print("")
            menu = self.u.grab("Please type the target Board ID:  ")
            if not menu: continue
            if menu.lower() == "m": return (self.target_macos,self.target_mac,self.target_mlb,self.latest_default)
            elif menu .lower() == "q": self.u.custom_quit()
            # Let's make sure we have a valid Mac-[8-16 hex] format
            if menu.lower().startswith("mac-"):
                menu = menu[4:]
            menu = menu.upper()
            if not len(menu) in (8,16) or not all((x in "0123456789ABCDEF" for x in menu)):
                continue
            # Got a valid format - return it and any matching macOS version
            model = "Mac-"+menu
            macos = self.boards.get(model,"Unknown")
            return (macos,model,self.target_mlb,self.latest_default)
    
    def input_mlb(self):
        while True:
            self.u.head("Input Custom MLB")
            print("")
            print("     Target macOS: {}".format(self.target_macos))
            print("  Target Board ID: {}".format(self.target_mac))
            print("       Target MLB: {}".format(self.target_mlb))
            print("   Latest/Default: {}".format(self.latest_default))
            print("")
            print("MLBs will be padded with 0s to 17 characters.")
            print("")
            print("M. Main Menu")
            print("Q. Quit")
            print("")
            menu = self.u.grab("Please type the target MLB:  ")
            if not menu: continue
            if menu.lower() == "m": return (self.target_macos,self.target_mac,self.target_mlb,self.latest_default)
            elif menu .lower() == "q": self.u.custom_quit()
            # Only allow alphanumeric chars, and pad to 17 with 0s
            if not menu.isalnum(): continue
            mlb = menu.upper().rjust(17,"0")
            return (self.target_macos,self.target_mac,mlb,self.latest_default)

    def select_target_recovery(self):
        os_list = list(self.recovery)[::-1] # Sort latest -> oldest
        while True:
            self.u.head("Select Target From recovery_urls.txt")
            print("")
            print("     Target macOS: {}".format(self.target_macos))
            print("  Target Board ID: {}".format(self.target_mac))
            print("       Target MLB: {}".format(self.target_mlb))
            print("   Latest/Default: {}".format(self.latest_default))
            print("")
            if not self.recovery:
                print("No macOS versions found!  Make sure recovery_urls.txt is in the Scripts")
                print("directory!")
                print("")
                self.u.grab("Press [enter] to return...")
                return (self.target_macos,self.target_mac,self.target_mlb,self.latest_default)
            for i,v in enumerate(os_list,start=1):
                print("{}. {} ({:,} total)".format(str(i).rjust(2),v,len(self.recovery[v])))
            print("")
            print("M. Main Menu")
            print("Q. Quit")
            print("")
            menu = self.u.grab("Please select an option:  ")
            if not menu: continue
            if menu.lower() == "m": return (self.target_macos,self.target_mac,self.target_mlb,self.latest_default)
            elif menu.lower() == "q": self.u.custom_quit()
            try:
                menu = int(menu)-1
                assert 0 <= menu < len(self.recovery)
            except:
                continue
            # We have a valid menu item - let's get the info needed
            macos = os_list[menu]
            index = 0
            if len(self.recovery[macos]) > 1:
                while True:
                    self.u.head("Select Board ID and MLB")
                    print("")
                    print("{} has {:,} urls:".format(macos,len(self.recovery[macos])))
                    print("")
                    for i,v in enumerate(self.recovery[macos],start=1):
                        print("{}. {} - {}".format(str(i),v["board_id"],v["mlb"]))
                    print("")
                    print("M. Main Menu")
                    print("Q. Quit")
                    print("")
                    menu = self.u.grab("Please select an option:  ")
                    if not menu: continue
                    if menu.lower() == "m": return (self.target_macos,self.target_mac,self.target_mlb,self.latest_default)
                    elif menu.lower() == "q": self.u.custom_quit()
                    try:
                        menu = int(menu)-1
                        assert 0 <= menu < len(self.recovery)
                    except:
                        continue
                    index = menu
                    break            
            model = self.recovery[macos][index]["board_id"]
            mlb   = self.recovery[macos][index]["mlb"]
            ld    = "latest" if "latest" in macos.lower() else "default"
            return (macos,model,mlb,ld)

    def download_macos(self):
        if not self.target_mac: return # wut
        self.u.head("Downloading macOS Recovery")
        print("")
        print("     Target macOS: {}".format(self.target_macos))
        print("  Target Board ID: {}".format(self.target_mac))
        print("       Target MLB: {}".format(self.target_mlb))
        print("   Latest/Default: {}".format(self.latest_default))
        print("")
        if os.path.exists(self.output):
            print("{} already exists - removing...".format(os.path.basename(self.output)))
            shutil.rmtree(self.output,ignore_errors=True)
        if not os.path.exists(self.output):
            print("Creating {}...".format(os.path.basename(self.output)))
            os.mkdir(self.output)
        args = [self.macrecovery_path,"-b",self.target_mac,"-m",self.target_mlb,"-o",self.output,"-os",self.latest_default]
        args.append("download")
        display_args = [os.path.basename(args[0])]+args[1:]
        print("")
        print("Running command:\n")
        print(" ".join(display_args))
        print("")
        out = self.r.run({"args":[sys.executable]+args,"stream":True})
        print("")
        self.u.grab("Press [enter] to return...")

    def main(self):
        self.u.head()
        print("")
        print("   macrecovery.py: {}".format("Located" if os.path.exists(self.macrecovery_path) else "NOT FOUND"))
        print("      boards.json: {}".format("Located" if os.path.exists(self.boards_path) else "NOT FOUND"))
        print("recovery_urls.txt: {}".format("Located" if os.path.exists(self.recovery_path) else "NOT FOUND"))
        print("")
        print("     Target macOS: {}".format(self.target_macos))
        print("  Target Board ID: {}".format(self.target_mac))
        print("       Target MLB: {}".format(self.target_mlb))
        print("   Latest/Default: {}".format(self.latest_default))
        print("")
        print("1. {} macrecovery.py, boards.json, and recovery_urls.txt".format("Update" if all((os.path.exists(x) for x in (self.recovery_path,self.macrecovery_path,self.boards_path))) else "Install"))
        print("2. Select Targets From recovery_urls.txt ({:,} available)".format(len(self.recovery)))
        print("3. Select Targets From boards.json ({:,} available)".format(len(set(self.boards.values()))))
        print("4. Input Custom Board ID")
        print("5. Input Custom MLB")
        print("6. Toggle Latest/Default")
        if self.target_mac and self.target_mlb:
            print("7. Download macOS Recovery For {}".format(self.target_mac))
        print("")
        print("Q. Quit")
        print("")
        menu = self.u.grab("Please select an option:  ")
        if not menu: return
        if menu.lower() == "q": self.u.custom_quit()
        elif menu == "1": self.update_macrecovery()
        elif menu == "2":
            self.target_macos,self.target_mac,self.target_mlb,self.latest_default = self.select_target_recovery()
        elif menu == "3":
            self.target_macos,self.target_mac,self.target_mlb,self.latest_default = self.select_target_macos()
        elif menu == "4":
            self.target_macos,self.target_mac,self.target_mlb,self.latest_default = self.input_mac_model()
        elif menu == "5" and self.target_mac:
            self.target_macos,self.target_mac,self.target_mlb,self.latest_default = self.input_mlb()
        elif menu == "6":
            self.latest_default = "latest" if self.latest_default == "default" else "default"
        elif menu == "7":
            self.download_macos()

if __name__ == '__main__':
    g = gibMacRecovery()
    while True:
        try:
            g.main()
        except Exception as e:
            print("An uncaught exception occurred:\n{}".format(e))
            print("")
            input("Press [enter] to continue...")
