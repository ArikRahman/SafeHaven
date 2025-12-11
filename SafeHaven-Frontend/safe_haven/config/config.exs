# This file is responsible for configuring your application
# and its dependencies with the aid of the Config module.
#
# This configuration file is loaded before any dependency and
# is restricted to this project.

# General application configuration
import Config

config :safe_haven,
  generators: [timestamp_type: :utc_datetime]

# Configure the endpoint
config :safe_haven, SafeHavenWeb.Endpoint,
  url: [host: "localhost"],
  adapter: Bandit.PhoenixAdapter,
  render_errors: [
    formats: [html: SafeHavenWeb.ErrorHTML, json: SafeHavenWeb.ErrorJSON],
    layout: false
  ],
  pubsub_server: SafeHaven.PubSub,
  live_view: [signing_salt: "ev75C+bJ"]



# Configure tailwind (the version is required)
config :tailwind,
  version: "4.1.12",
  safe_haven: [
    args: ~w(
      --input=assets/css/app.css
      --output=priv/static/assets/css/app.css
    ),
    cd: Path.expand("..", __DIR__)
  ]

# Configure Elixir's Logger
config :logger, :default_formatter,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

# Use Jason for JSON parsing in Phoenix
config :phoenix, :json_library, Jason

# Import environment specific config. This must remain at the bottom
# of this file so it overrides the configuration defined above.
import_config "#{config_env()}.exs"
