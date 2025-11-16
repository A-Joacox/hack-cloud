# Realtime Service (WebSocket + Streams + SNS)

This package deploys a minimal realtime stack:
- API Gateway WebSocket with `$connect` and `$disconnect` routes.
- DynamoDB `Connections` table to track client sessions.
- `Broadcaster` Lambda to fan-out updates from the Incidents table stream to WebSocket clients.
- `Notifier` Lambda to publish alerts to an SNS topic for authorities.

It does NOT create the `Incidents` table. Pass its DynamoDB Stream ARN when deploying.

## Prerequisites
- AWS account + credentials configured (`aws configure`).
- AWS SAM CLI installed.
- The backend `Incidents` table with DynamoDB Streams enabled (NEW_AND_OLD_IMAGES recommended).

## Deploy (PowerShell)
```powershell
cd services/realtime
sam build
sam deploy --guided
# When prompted, set Parameter IncidentsStreamArn to your Incidents table Stream ARN (can be empty to deploy without bindings).
```

You can deploy without the stream parameter first. After the backend enables Streams, update the stack:
```powershell
sam deploy \
  --stack-name alerta-realtime \
  --parameter-overrides IncidentsStreamArn="<YOUR_INCIDENTS_STREAM_ARN>"
```

## Outputs (copy for your frontend)
- `WebSocketWssEndpoint`: use this URL in the web app (`wss://.../prod`).
- `WebSocketManagementUrl`: used internally by the Broadcaster Lambda to call `post_to_connection`.

## Environment
- `BroadcasterFunction`: `CONNECTIONS_TABLE`, `WS_CALLBACK_URL` (auto-set).
- `NotifierFunction`: `SNS_TOPIC_ARN` (auto-set).
- `Connect/Disconnect`: `CONNECTIONS_TABLE` (auto-set).

## Handlers
- `src/connection_manager.py:on_connect` / `on_disconnect` – persist/remove connection: `{ pk: "CONN#<id>", sk: "META#" }` plus `userId`, `role`.
- `src/broadcaster.py:handler` – reads stream records (INSERT/MODIFY), builds payload and posts via API GW management.
- `src/notifier.py:handler` – publishes to SNS when urgency is high or status escalates.

## Testing locally (invoke)
```powershell
sam build
sam local invoke ConnectFunction --event events/connect.json
sam local invoke BroadcasterFunction --event events/stream-insert.json
```

Create your own `events/*` JSON as needed. For end-to-end, deploy and connect a WebSocket client to `WebSocketWssEndpoint`.
