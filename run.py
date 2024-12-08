from app import create_app
import colorama
from colorama import Fore, Style

# Initialize colorama for colored output
colorama.init()

app = create_app()

if __name__ == '__main__':
    print(f"\n{Fore.GREEN}========================================")
    print(f"🚀 F13 HRMS Application - Default Credentials")
    print(f"========================================{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Admin Login:")
    print(f"Email: {Fore.CYAN}admin@f13.com")
    print(f"Password: {Fore.CYAN}admin123{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Employee Default Password: {Fore.CYAN}employee123{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}========================================")
    print(f"Access the application at: {Fore.CYAN}http://127.0.0.1:5000{Style.RESET_ALL}")
    print(f"{Fore.GREEN}========================================\n{Style.RESET_ALL}")
    
    app.run(debug=True)
    #To run in EC2
    #app.run(host='0.0.0.0' , port=5000, debug=True)
