# Diagrama de Classes

```mermaid
classDiagram
    class Flask {
        +route()
        +run()
    }
    
    class AppConfig {
        +SECRET_KEY
        +MYSQL_HOST
        +MYSQL_USER
        +MYSQL_DB
        +EMAIL_SENDER
    }
    
    class DatabaseService {
        +get_db_connection()
    }
    
    class EmailService {
        +send_email()
        +email_logger
    }
    
    class Routes {
        +index()
        +sobre()
        +pontos_coleta()
        +cadastro()
        +admin_login()
        +logado()
    }
    
    class API {
        +api_pontos_coleta()
        +api_solicitar_cadastro()
    }
    
    Routes --> DatabaseService: uses
    API --> DatabaseService: uses
    API --> EmailService: uses
    Flask <|-- AppConfig: extends
    AppConfig *-- DatabaseService: contains
    AppConfig *-- EmailService: contains
    AppConfig o-- Routes: configures
    AppConfig o-- API: configures
    Routes --> EmailService: may use