from ai.query_processor.models import Technology, TechnologyType


class EntityRegistry:
    _instance = None
    _initialized: bool

    def __new__(cls) -> "EntityRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._languages: dict[str, Technology] = {}
        self._frameworks: dict[str, Technology] = {}
        self._libraries: dict[str, Technology] = {}
        self._tools: dict[str, Technology] = {}
        self._databases: dict[str, Technology] = {}
        self._platforms: dict[str, Technology] = {}
        self._categories: dict[str, str] = {}
        self._synonyms: dict[str, str] = {}
        self._abbreviations: dict[str, str] = {}
        self._populate()

    def _populate(self) -> None:
        self._populate_languages()
        self._populate_frameworks()
        self._populate_libraries()
        self._populate_tools()
        self._populate_databases()
        self._populate_platforms()
        self._populate_categories()
        self._populate_synonyms()
        self._populate_abbreviations()

    def _populate_languages(self) -> None:
        entries = [
            ("Python", ["py", "python3", "python2"]),
            ("JavaScript", ["js", "nodejs", "node", "ecmascript", "es6", "es2015"]),
            ("TypeScript", ["ts", "typescript"]),
            ("Rust", ["rust", "rust-lang", "rs"]),
            ("Go", ["golang", "go-lang"]),
            ("Java", ["java", "jvm"]),
            ("C++", ["cpp", "c-plus-plus", "cplusplus", "cxx"]),
            ("C", ["c-lang"]),
            ("C#", ["csharp", "c-sharp", "dotnet"]),
            ("Ruby", ["ruby", "rb", "ruby-lang"]),
            ("PHP", ["php", "php-lang"]),
            ("Swift", ["swift-lang"]),
            ("Kotlin", ["kotlin", "kt"]),
            ("Scala", ["scala-lang"]),
            ("R", ["r-lang", "r-language"]),
            ("Dart", ["dart-lang"]),
            ("Elixir", ["elixir-lang"]),
            ("Haskell", ["haskell-lang"]),
            ("Lua", ["lua-lang"]),
            ("Perl", ["perl-lang"]),
            ("Zig", ["zig-lang"]),
            ("Clojure", ["clojure-lang"]),
            ("Solidity", ["solidity-lang"]),
            ("Assembly", ["asm", "assembly-lang"]),
            ("Shell", ["bash", "zsh", "sh", "shell-script"]),
            ("SQL", ["sql-lang", "plsql"]),
            ("MATLAB", ["matlab-lang"]),
            ("Julia", ["julia-lang"]),
            ("Objective-C", ["objc", "objective-c"]),
            ("Groovy", ["groovy-lang"]),
            ("COBOL", ["cobol-lang"]),
            ("Fortran", ["fortran-lang"]),
            ("Delphi", ["delphi-lang", "pascal"]),
            ("Visual Basic", ["vb", "vb.net"]),
            ("F#", ["fsharp", "f-sharp"]),
        ]
        for name, aliases in entries:
            t = Technology(
                name=name, type=TechnologyType.LANGUAGE,
                aliases=aliases, category="language",
            )
            self._languages[name.lower()] = t
            for a in aliases:
                self._languages[a.lower()] = t

    def _populate_frameworks(self) -> None:
        web_frontend = [
            ("React", ["reactjs", "react.js", "react-js"]),
            ("Vue.js", ["vue", "vuejs", "vue-js", "vue2", "vue3"]),
            ("Angular", ["angularjs", "angular.io", "ng"]),
            ("Svelte", ["sveltejs", "svelte-js"]),
            ("Solid.js", ["solidjs", "solid-js"]),
            ("Preact", ["preactjs"]),
            ("Next.js", ["nextjs", "next-js"]),
            ("Nuxt.js", ["nuxtjs", "nuxt-js"]),
            ("Gatsby", ["gatsbyjs", "gatsby-js"]),
            ("Astro", ["astrojs", "astro-js"]),
            ("Qwik", ["qwikjs", "qwik-js"]),
            ("Remix", ["remixjs", "remix-run"]),
            ("Ember.js", ["emberjs", "ember-js"]),
            ("Backbone.js", ["backbonejs", "backbone-js"]),
            ("Lit", ["lit-html", "lit-element"]),
            ("Alpine.js", ["alpinejs", "alpine-js"]),
            ("Stencil", ["stenciljs"]),
            ("jQuery", ["jquery", "jquery-js"]),
            ("Bootstrap", ["bootstrap-css", "bootstrap4", "bootstrap5"]),
            ("Tailwind CSS", ["tailwind", "tailwindcss"]),
            ("Material UI", ["mui", "material-design", "materialize"]),
            ("Chakra UI", ["chakra-ui"]),
            ("Semantic UI", ["semantic-ui"]),
        ]
        web_backend = [
            ("Django", ["django-framework"]),
            ("Flask", ["flask-framework"]),
            ("FastAPI", ["fast-api"]),
            ("Spring Boot", ["spring", "spring-framework", "spring-boot"]),
            ("Ruby on Rails", ["rails", "ror", "ruby-rails"]),
            ("Laravel", ["laravel-framework"]),
            ("Express.js", ["express", "express-js", "expressjs"]),
            ("Koa.js", ["koa", "koa-js"]),
            ("NestJS", ["nest", "nest-js", "nestjs"]),
            ("ASP.NET Core", ["asp.net", "dotnet-core", "dotnet"]),
            ("Phoenix", ["phoenix-framework", "elixir-phoenix"]),
            ("Actix Web", ["actix", "actix-web"]),
            ("Rocket", ["rocket-framework", "rust-rocket"]),
            ("Tornado", ["tornado-framework"]),
            ("Pyramid", ["pyramid-framework"]),
            ("Falcon", ["falcon-framework"]),
            ("Sanic", ["sanic-framework"]),
            ("Yii", ["yii-framework"]),
            ("Symfony", ["symfony-framework"]),
            ("CodeIgniter", ["codeigniter-framework"]),
            ("CakePHP", ["cakephp-framework"]),
            ("Gin", ["gin-gonic", "gin-framework"]),
            ("Echo", ["echo-framework", "labstack-echo"]),
            ("Fiber", ["fiber-framework", "gofiber"]),
        ]
        mobile = [
            ("Flutter", ["flutter-framework"]),
            ("React Native", ["react-native", "rn"]),
            ("Ionic", ["ionic-framework"]),
            ("Xamarin", ["xamarin-framework"]),
            ("Android SDK", ["android-framework", "android-sdk"]),
            ("SwiftUI", ["swift-ui"]),
            ("UIKit", ["uikit-framework"]),
            ("Capacitor", ["capacitor-framework"]),
            ("NativeScript", ["nativescript-framework"]),
            ("Expo", ["expo-framework"]),
        ]
        data_science = [
            ("TensorFlow", ["tensorflow", "tf"]),
            ("PyTorch", ["pytorch", "torch"]),
            ("JAX", ["jax-framework"]),
            ("Keras", ["keras-framework"]),
            ("Scikit-learn", ["sklearn", "scikit-learn"]),
            ("Hugging Face Transformers", ["transformers", "huggingface", "hf"]),
            ("LangChain", ["langchain-framework"]),
            ("LlamaIndex", ["llama-index"]),
            ("OpenCV", ["opencv-framework", "cv2"]),
            ("Apache Spark MLlib", ["spark-mllib", "mllib"]),
            ("Pandas", ["pandas-library"]),
            ("NumPy", ["numpy-library"]),
            ("DVC", ["dvc-framework"]),
            ("MLflow", ["mlflow-framework"]),
            ("Weights & Biases", ["wandb", "weights-biases"]),
        ]
        testing = [
            ("Jest", ["jest-framework"]),
            ("pytest", ["pytest-framework"]),
            ("Mocha", ["mocha-framework"]),
            ("JUnit", ["junit-framework"]),
            ("Cypress", ["cypress-framework"]),
            ("Playwright", ["playwright-framework"]),
            ("Selenium", ["selenium-framework"]),
            ("Vitest", ["vitest-framework"]),
        ]
        desktop = [
            ("Electron", ["electron-framework"]),
            ("Tauri", ["tauri-framework"]),
            ("Qt", ["qt-framework"]),
            ("GTK", ["gtk-framework"]),
            ("WPF", ["wpf-framework"]),
            ("WinForms", ["winforms-framework"]),
            (".NET MAUI", ["maui", "dotnet-maui"]),
            ("JavaFX", ["javafx-framework"]),
            ("Swing", ["swing-framework"]),
        ]
        all_entries: list[tuple[str, list[str]]] = (
            web_frontend + web_backend + mobile + data_science + testing + desktop
        )
        for name, aliases in all_entries if False else []:  # type: ignore[var-annotated]
            pass
        for name, aliases in all_entries:
            t = Technology(
                name=name, type=TechnologyType.FRAMEWORK,
                aliases=aliases, category="framework",
            )
            self._frameworks[name.lower()] = t
            for a in aliases:
                self._frameworks[a.lower()] = t

    def _populate_libraries(self) -> None:
        entries = [
            ("Lodash", ["lodash-lib", "underscore"]),
            ("Axios", ["axios-lib"]),
            ("Redux", ["redux-lib", "react-redux"]),
            ("Zustand", ["zustand-lib"]),
            ("React Query", ["tanstack-query", "react-query"]),
            ("NextAuth.js", ["nextauth", "next-auth"]),
            ("Prisma", ["prisma-orm"]),
            ("TypeORM", ["typeorm-lib"]),
            ("SQLAlchemy", ["sqlalchemy-orm"]),
            ("Mongoose", ["mongoose-orm"]),
            ("Sequelize", ["sequelize-orm"]),
            ("Drizzle ORM", ["drizzle-orm"]),
            ("D3.js", ["d3", "d3js"]),
            ("Chart.js", ["chartjs", "chart-js"]),
            ("Three.js", ["threejs", "three-js"]),
            ("Anime.js", ["animejs", "anime-js"]),
            ("GSAP", ["gsap-lib"]),
            ("Framer Motion", ["framer-motion"]),
            ("React Router", ["react-router"]),
            ("React Hook Form", ["react-hook-form"]),
            ("Formik", ["formik-lib"]),
            ("Yup", ["yup-validation"]),
            ("Zod", ["zod-validation"]),
            ("Joi", ["joi-validation"]),
            ("Socket.IO", ["socketio", "socket-io", "socket.io"]),
            ("Webpack", ["webpack-bundler"]),
            ("Vite", ["vite-bundler"]),
            ("esbuild", ["esbuild-bundler"]),
            ("Parcel", ["parcel-bundler"]),
            ("Rollup", ["rollup-bundler"]),
            ("Babel", ["babel-compiler"]),
            ("SWC", ["swc-compiler"]),
            ("ESLint", ["eslint-linter"]),
            ("Prettier", ["prettier-formatter"]),
            ("Nginx", ["nginx-server"]),
            ("Apache HTTPD", ["apache-server", "httpd"]),
            ("Caddy", ["caddy-server"]),
            ("HAProxy", ["haproxy-lb"]),
            ("Celery", ["celery-queue"]),
            ("Redis", ["redis-cache"]),
            ("Memcached", ["memcached-cache"]),
            ("RabbitMQ", ["rabbitmq-queue"]),
            ("Kafka", ["apache-kafka"]),
            ("gRPC", ["grpc-framework"]),
            ("GraphQL", ["graphql-lib"]),
            ("Apollo", ["apollo-client", "apollo-server"]),
            ("Protobuf", ["protobuf-lib", "protocol-buffers"]),
            ("OpenAPI", ["swagger", "openapi-spec"]),
            ("FFmpeg", ["ffmpeg-lib"]),
            ("ImageMagick", ["imagemagick-lib"]),
            ("Tesseract OCR", ["tesseract-ocr"]),
            ("Tika", ["apache-tika"]),
            ("PDF.js", ["pdfjs", "pdf-js"]),
            ("Puppeteer", ["puppeteer-lib"]),
            ("Cheerio", ["cheerio-lib"]),
            ("Beautiful Soup", ["beautifulsoup", "bs4"]),
            ("Scrapy", ["scrapy-framework"]),
        ]
        for name, aliases in entries:
            t = Technology(
                name=name, type=TechnologyType.LIBRARY,
                aliases=aliases, category="library",
            )
            self._libraries[name.lower()] = t
            for a in aliases:
                self._libraries[a.lower()] = t

    def _populate_tools(self) -> None:
        entries = [
            ("Git", ["vcs", "version-control"]),
            ("Docker", ["dockerize", "container"]),
            ("Kubernetes", ["k8s", "kube"]),
            ("Terraform", ["terraform-iac"]),
            ("Ansible", ["ansible-automation"]),
            ("Jenkins", ["jenkins-ci"]),
            ("GitHub Actions", ["gh-actions", "github-ci"]),
            ("GitLab CI", ["gitlab-ci"]),
            ("CircleCI", ["circle-ci"]),
            ("Travis CI", ["travis-ci"]),
            ("Prometheus", ["prometheus-monitor"]),
            ("Grafana", ["grafana-dash"]),
            ("ELK Stack", ["elastic-stack", "elasticsearch"]),
            ("Jaeger", ["jaeger-tracing"]),
            ("Postman", ["postman-api"]),
            ("Insomnia", ["insomnia-api"]),
            ("VS Code", ["vscode", "visual-studio-code"]),
            ("Neovim", ["nvim", "neovim-editor"]),
            ("Helm", ["helm-chart"]),
            ("Vagrant", ["vagrant-vm"]),
            ("Minikube", ["minikube-k8s"]),
        ]
        for name, aliases in entries:
            t = Technology(name=name, type=TechnologyType.TOOL, aliases=aliases, category="tool")
            self._tools[name.lower()] = t
            for a in aliases:
                self._tools[a.lower()] = t

    def _populate_databases(self) -> None:
        entries = [
            ("PostgreSQL", ["postgres", "psql", "pgsql"]),
            ("MySQL", ["mysql-db"]),
            ("MariaDB", ["mariadb-db"]),
            ("SQLite", ["sqlite-db"]),
            ("MongoDB", ["mongo-db", "mongo"]),
            ("Redis", ["redis-db"]),
            ("Cassandra", ["cassandra-db"]),
            ("Elasticsearch", ["elastic-db", "elastic-search"]),
            ("DynamoDB", ["dynamo-db", "dynamodb"]),
            ("Firebase", ["firebase-db", "firestore"]),
            ("Supabase", ["supabase-db"]),
            ("Neo4j", ["neo4j-graph"]),
            ("ArangoDB", ["arango-db"]),
            ("CouchDB", ["couch-db"]),
            ("ClickHouse", ["clickhouse-db"]),
            ("InfluxDB", ["influx-db"]),
            ("TimescaleDB", ["timescale-db"]),
            ("CockroachDB", ["cockroach-db"]),
            ("ScyllaDB", ["scylla-db"]),
            ("Pinecone", ["pinecone-vector"]),
            ("Weaviate", ["weaviate-vector"]),
            ("Qdrant", ["qdrant-vector"]),
            ("Milvus", ["milvus-vector"]),
            ("Chroma", ["chroma-vector"]),
        ]
        for name, aliases in entries:
            t = Technology(
                name=name, type=TechnologyType.DATABASE,
                aliases=aliases, category="database",
            )
            self._databases[name.lower()] = t
            for a in aliases:
                self._databases[a.lower()] = t

    def _populate_platforms(self) -> None:
        entries = [
            ("Linux", ["gnu-linux", "ubuntu", "debian", "centos", "fedora", "arch", "alpine"]),
            ("macOS", ["mac", "osx", "mac-os", "darwin"]),
            ("Windows", ["win", "windows-os"]),
            ("Android", ["android-os"]),
            ("iOS", ["iphone", "ipad", "apple-mobile"]),
            ("Web", ["browser", "web-browser"]),
            ("Cloud", ["aws", "gcp", "azure", "cloud-computing"]),
            ("AWS", ["amazon-web-services", "ec2", "s3", "lambda"]),
            ("Google Cloud", ["gcp", "google-cloud-platform"]),
            ("Azure", ["microsoft-azure"]),
            ("Heroku", ["heroku-paas"]),
            ("Vercel", ["vercel-serverless"]),
            ("Netlify", ["netlify-hosting"]),
            ("Cloudflare", ["cloudflare-workers", "cf"]),
            ("Docker", ["docker-platform"]),
            ("Kubernetes", ["k8s-platform", "kube-platform"]),
            ("Serverless", ["lambda-serverless", "faas"]),
            ("Edge", ["edge-computing", "edge-network"]),
        ]
        for name, aliases in entries:
            t = Technology(
                name=name, type=TechnologyType.PLATFORM,
                aliases=aliases, category="platform",
            )
            self._platforms[name.lower()] = t
            for a in aliases:
                self._platforms[a.lower()] = t

    def _populate_categories(self) -> None:
        categories = [
            ("video editor", "video editing", "Video Editing Software"),
            ("video editing", "video editing", "Video Editing Software"),
            ("photo editor", "photo editing", "Photo Editing Software"),
            ("image editor", "photo editing", "Photo Editing Software"),
            ("password manager", "password management", "Password Manager"),
            ("password management", "password management", "Password Manager"),
            ("chatbot", "chatbot", "AI Chatbot"),
            ("ai chatbot", "chatbot", "AI Chatbot"),
            ("expense tracker", "expense tracking", "Expense Tracker"),
            ("budget tracker", "expense tracking", "Expense Tracker"),
            ("portfolio", "portfolio", "Portfolio Website"),
            ("portfolio website", "portfolio", "Portfolio Website"),
            ("ocr", "ocr", "OCR Tool"),
            ("ocr tool", "ocr", "OCR Tool"),
            ("optical character recognition", "ocr", "OCR Tool"),
            ("hospital management", "healthcare", "Hospital Management System"),
            ("hospital management system", "healthcare", "Hospital Management System"),
            ("compiler", "compiler", "Compiler"),
            ("image compression", "image processing", "Image Compression Library"),
            ("music streaming", "music", "Music Streaming App"),
            ("music player", "music", "Music Player"),
            ("video player", "video", "Video Player"),
            ("code editor", "code editor", "Code Editor"),
            ("ide", "code editor", "Integrated Development Environment"),
            ("text editor", "code editor", "Text Editor"),
            ("crm", "crm", "Customer Relationship Management"),
            ("customer relationship management", "crm", "Customer Relationship Management"),
            ("erp", "erp", "Enterprise Resource Planning"),
            ("enterprise resource planning", "erp", "Enterprise Resource Planning"),
            ("cms", "cms", "Content Management System"),
            ("content management", "cms", "Content Management System"),
            ("blog", "blogging", "Blogging Platform"),
            ("ecommerce", "ecommerce", "E-Commerce Platform"),
            ("e-commerce", "ecommerce", "E-Commerce Platform"),
            ("shopping", "ecommerce", "E-Commerce Platform"),
            ("analytics", "analytics", "Analytics Tool"),
            ("dashboard", "dashboard", "Dashboard"),
            ("scheduler", "scheduling", "Scheduler"),
            ("calendar", "scheduling", "Calendar App"),
            ("todo", "productivity", "To-Do App"),
            ("to-do", "productivity", "To-Do App"),
            ("task manager", "productivity", "Task Manager"),
            ("note taking", "note taking", "Note Taking App"),
            ("notes", "note taking", "Note Taking App"),
            ("diagram", "diagramming", "Diagram Tool"),
            ("flowchart", "diagramming", "Flowchart Tool"),
            ("mind map", "diagramming", "Mind Mapping Tool"),
            ("data visualization", "data viz", "Data Visualization Library"),
            ("chart", "data viz", "Charting Library"),
            ("graph", "data viz", "Graphing Library"),
            ("machine learning", "machine learning", "Machine Learning Framework"),
            ("deep learning", "deep learning", "Deep Learning Framework"),
            ("nlp", "nlp", "NLP Library"),
            ("natural language processing", "nlp", "NLP Library"),
            ("computer vision", "computer vision", "Computer Vision Library"),
            ("data pipeline", "data engineering", "Data Pipeline Tool"),
            ("etl", "data engineering", "ETL Tool"),
            ("data warehouse", "data engineering", "Data Warehouse"),
            ("orm", "orm", "ORM Library"),
            ("object relational mapping", "orm", "ORM Library"),
            ("api gateway", "api", "API Gateway"),
            ("rest api", "api", "REST API Framework"),
            ("graphql api", "api", "GraphQL API"),
            ("web framework", "web framework", "Web Framework"),
            ("static site", "static site", "Static Site Generator"),
            ("ssg", "static site", "Static Site Generator"),
            ("search engine", "search", "Search Engine"),
            ("full text search", "search", "Full-Text Search Engine"),
            ("logging", "logging", "Logging Library"),
            ("monitoring", "monitoring", "Monitoring Tool"),
            ("testing", "testing", "Testing Framework"),
            ("unit testing", "testing", "Unit Testing Framework"),
            ("e2e testing", "testing", "End-to-End Testing Framework"),
            ("load testing", "testing", "Load Testing Tool"),
            ("api testing", "testing", "API Testing Tool"),
            ("documentation", "docs", "Documentation Tool"),
            ("wiki", "docs", "Wiki Software"),
            ("forms", "forms", "Form Builder"),
            ("survey", "forms", "Survey Tool"),
            ("authentication", "auth", "Authentication Library"),
            ("authorization", "auth", "Authorization Library"),
            ("payment", "payments", "Payment Gateway"),
            ("invoicing", "billing", "Invoicing Software"),
            ("chat", "messaging", "Chat Application"),
            ("messaging", "messaging", "Messaging App"),
            ("video conferencing", "video call", "Video Conferencing Tool"),
            ("screenshot", "screenshot", "Screenshot Tool"),
            ("screen recorder", "screen recording", "Screen Recorder"),
            ("file sharing", "file sharing", "File Sharing Tool"),
            ("cloud storage", "file sharing", "Cloud Storage"),
            ("backup", "backup", "Backup Tool"),
            ("game engine", "game dev", "Game Engine"),
            ("game development", "game dev", "Game Development Framework"),
        ]
        self._categories = {}
        for term, domain, display_name in categories:
            self._categories[term.lower()] = domain
            self._categories[display_name.lower()] = domain

    def _populate_synonyms(self) -> None:
        self._synonyms = {
            "ai": "artificial intelligence",
            "ml": "machine learning",
            "dl": "deep learning",
            "nlp": "natural language processing",
            "cv": "computer vision",
            "db": "database",
            "cli": "command line interface",
            "gui": "graphical user interface",
            "ui": "user interface",
            "ux": "user experience",
            "api": "application programming interface",
            "orm": "object relational mapping",
            "ssg": "static site generator",
            "spa": "single page application",
            "pwa": "progressive web app",
            "cms": "content management system",
            "crm": "customer relationship management",
            "erp": "enterprise resource planning",
            "saas": "software as a service",
            "paas": "platform as a service",
            "iaas": "infrastructure as a service",
            "faas": "function as a service",
            "k8s": "kubernetes",
            "vm": "virtual machine",
            "ci": "continuous integration",
            "cd": "continuous deployment",
            "cicd": "continuous integration and deployment",
            "ioc": "inversion of control",
            "di": "dependency injection",
            "tdd": "test driven development",
            "bdd": "behavior driven development",
            "dddd": "domain driven design",
            "mvvm": "model view viewmodel",
            "mvc": "model view controller",
            "mvp": "model view presenter",
            "rest": "representational state transfer",
            "grpc": "google remote procedure call",
            "jwt": "json web token",
            "json": "javascript object notation",
            "yaml": "yaml ain't markup language",
            "csv": "comma separated values",
            "pdf": "portable document format",
            "html": "hypertext markup language",
            "css": "cascading style sheets",
            "sql": "structured query language",
            "nosql": "not only sql",
            "ts": "typescript",
            "js": "javascript",
            "py": "python",
            "rb": "ruby",
            "rs": "rust",
            "kt": "kotlin",
            "go": "golang",
            "tf": "tensorflow",
            "rn": "react native",
            "npm": "node package manager",
            "yarn": "yarn package manager",
            "pnpm": "pnpm package manager",
            "pip": "pip package manager",
            "conda": "conda package manager",
            "docker": "docker container",
            "vscode": "visual studio code",
            "ide": "integrated development environment",
        }

    def _populate_abbreviations(self) -> None:
        self._abbreviations = {
            "app": "application",
            "repo": "repository",
            "lib": "library",
            "config": "configuration",
            "auth": "authentication",
            "dev": "development",
            "prod": "production",
            "docs": "documentation",
            "specs": "specifications",
            "info": "information",
            "admin": "administration",
            "img": "image",
            "msg": "message",
            "sync": "synchronization",
            "async": "asynchronous",
            "calc": "calculator",
            "gen": "generator",
            "util": "utility",
            "mgr": "manager",
            "svc": "service",
            "dept": "department",
            "org": "organization",
            "deploy": "deployment",
            "env": "environment",
            "param": "parameter",
            "expr": "expression",
            "stmt": "statement",
            "attr": "attribute",
            "prop": "property",
            "val": "value",
            "var": "variable",
            "func": "function",
            "impl": "implementation",
            "pkg": "package",
            "src": "source",
            "dest": "destination",
            "tmp": "temporary",
        }

    # --- Public API ---

    @property
    def all_known_terms(self) -> set[str]:
        terms: set[str] = set()
        for d in [
            self._languages, self._frameworks, self._libraries,
            self._tools, self._databases, self._platforms,
        ]:
            terms.update(d.keys())
        terms.update(self._categories.keys())
        terms.update(self._synonyms.keys())
        terms.update(self._abbreviations.keys())
        return terms

    def resolve_entity(self, term: str) -> Technology | None:
        key = term.lower().strip()
        for lookup in [
            self._languages, self._frameworks, self._libraries,
            self._tools, self._databases, self._platforms,
        ]:
            if key in lookup:
                return lookup[key]
        return None

    def resolve_synonym(self, term: str) -> str | None:
        key = term.lower().strip()
        if key in self._synonyms:
            return self._synonyms[key]
        return None

    def resolve_abbreviation(self, term: str) -> str | None:
        key = term.lower().strip()
        if key in self._abbreviations:
            return self._abbreviations[key]
        return None

    def resolve_category(self, term: str) -> str | None:
        key = term.lower().strip()
        if key in self._categories:
            return self._categories[key]
        return None

    def get_category_display(self, term: str) -> str | None:
        key = term.lower().strip()
        if key in self._categories:
            return self._categories[key]
        return None

    def search_entities(self, query: str) -> list[tuple[str, Technology, float]]:
        query_lower = query.lower()
        results = []
        for lookup, source in [
            (self._languages, "language"),
            (self._frameworks, "framework"),
            (self._libraries, "library"),
            (self._tools, "tool"),
            (self._databases, "database"),
            (self._platforms, "platform"),
        ]:
            for key, tech in lookup.items():
                if key in query_lower:
                    score = len(key) / len(query_lower) if query_lower else 0
                    results.append((key, tech, min(score + 0.3, 1.0)))
        results.sort(key=lambda x: -x[2])
        seen = set()
        deduped = []
        for key, tech, score in results:
            if tech.name not in seen:
                seen.add(tech.name)
                deduped.append((key, tech, score))
        return deduped
