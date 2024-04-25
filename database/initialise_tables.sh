read -p "Are you sure you want to run this script? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Script execution aborted."
    exit 1
fi

source .env
export PGPASSWORD=$DB_PASS
psql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME -f schema.sql