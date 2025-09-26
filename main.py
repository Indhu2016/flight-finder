import argparse
from rich import print as rprint
from src.tools.formatters import human_readable
from src.tools.emailer import send_itinerary_email
from src.agents.route_agent import plan_best_routes
from src.tools.security import validate_email, sanitize_city_name, validate_date, validate_numeric_input

def parse_args():
    ap = argparse.ArgumentParser(description="Smart Travel Optimizer")
    ap.add_argument("--origin", required=True, help="Origin city")
    ap.add_argument("--destination", required=True, help="Destination city")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--bags", type=int, default=2, help="Minimum checked bags required")
    ap.add_argument("--max-connections", type=int, default=2, help="Maximum allowed connections")
    ap.add_argument("--w-time", type=float, default=0.6, help="Weight on time (0-1)")
    ap.add_argument("--w-cost", type=float, default=0.4, help="Weight on cost (0-1)")
    ap.add_argument("--email", help="Send results to this email address")
    return ap.parse_args()

def main():
    args = parse_args()
    
    try:
        # Validate inputs
        clean_origin = sanitize_city_name(args.origin)
        clean_destination = sanitize_city_name(args.destination)
        
        if not validate_date(args.date):
            rprint("[red]Error: Invalid date format. Use YYYY-MM-DD[/red]")
            return
        
        if not validate_numeric_input(args.bags, 0, 10):
            rprint("[red]Error: Invalid number of bags. Must be between 0 and 10.[/red]")
            return
        
        if not validate_numeric_input(args.max_connections, 0, 5):
            rprint("[red]Error: Invalid number of connections. Must be between 0 and 5.[/red]")
            return
        
        if not validate_numeric_input(args.w_time, 0, 1):
            rprint("[red]Error: Time weight must be between 0 and 1.[/red]")
            return
        
        if not validate_numeric_input(args.w_cost, 0, 1):
            rprint("[red]Error: Cost weight must be between 0 and 1.[/red]")
            return
        
        if args.email and not validate_email(args.email):
            rprint("[red]Error: Invalid email address format.[/red]")
            return

        results = plan_best_routes(
            origin=clean_origin,
            destination=clean_destination,
            date=args.date,
            min_checked_bags=args.bags,
            max_connections=args.max_connections,
            w_time=args.w_time,
            w_cost=args.w_cost
        )

        if not results:
            rprint("[yellow]No matching routes. Try relaxing filters or changing date.[/yellow]")
            return

        rprint("[bold green]Top options:[/bold green]")
        rprint(human_readable(results[:5]))

        if args.email:
            try:
                send_itinerary_email(args.email, clean_origin, clean_destination, args.date, results)
                rprint("[green]Email sent successfully![/green]")
            except Exception as e:
                rprint(f"[red]Failed to send email: {str(e)}[/red]")
                
    except ValueError as e:
        rprint(f"[red]Input validation error: {str(e)}[/red]")
    except Exception as e:
        rprint(f"[red]An error occurred: {str(e)}[/red]")

if __name__ == "__main__":
    main()
