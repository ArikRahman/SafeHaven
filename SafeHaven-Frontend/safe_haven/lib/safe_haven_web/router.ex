defmodule SafeHavenWeb.Router do
  use SafeHavenWeb, :router

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_live_flash
    plug :put_root_layout, html: {SafeHavenWeb.Layouts, :root}
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/", SafeHavenWeb do
    pipe_through :browser

    get "/", PageController, :home
    get "/motor", PageController, :motor
    post "/motor/run", PageController, :run_motor
    post "/run", PageController, :run_motor
    get "/heatmaps", PageController, :heatmaps
    post "/heatmaps/run", PageController, :run_heatmaps
    get "/terminal", PageController, :terminal
    post "/terminal", PageController, :run_terminal
  end

  # Other scopes may use custom stacks.
  # scope "/api", SafeHavenWeb do
  #   pipe_through :api
  # end
end
