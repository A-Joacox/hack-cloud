#!/bin/bash
# Script de deploy completo para AlertaUTEC en AWS Academy

set -e

echo "🚀 AlertaUTEC - Deploy Completo en AWS"
echo "======================================"
echo ""

# Configuración
REGION="us-east-1"
LAB_ROLE_ARN="arn:aws:iam::527785891672:role/LabRole"
INCIDENTS_TABLE="AlertaUTEC-Incidents"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Paso 1: Crear tabla DynamoDB con Streams${NC}"
if aws dynamodb describe-table --table-name $INCIDENTS_TABLE --region $REGION 2>/dev/null; then
    echo "✅ Tabla $INCIDENTS_TABLE ya existe"
else
    aws dynamodb create-table \
        --table-name $INCIDENTS_TABLE \
        --attribute-definitions AttributeName=id,AttributeType=S \
        --key-schema AttributeName=id,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
        --region $REGION
    echo "⏳ Esperando a que la tabla esté activa..."
    aws dynamodb wait table-exists --table-name $INCIDENTS_TABLE --region $REGION
    echo "✅ Tabla $INCIDENTS_TABLE creada"
fi

# Obtener Stream ARN
STREAM_ARN=$(aws dynamodb describe-table \
    --table-name $INCIDENTS_TABLE \
    --query 'Table.LatestStreamArn' \
    --output text \
    --region $REGION)
echo "Stream ARN: $STREAM_ARN"
echo ""

echo -e "${YELLOW}Paso 2: Desplegar servicio de tiempo real (WebSocket + SNS)${NC}"
cd services/realtime
sam build --template template-academy.yaml --use-container
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name alerta-realtime \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        LabRoleArn=$LAB_ROLE_ARN \
        IncidentsStreamArn="$STREAM_ARN" \
    --resolve-s3 \
    --region $REGION \
    --no-confirm-changeset

WS_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name alerta-realtime \
    --query 'Stacks[0].Outputs[?OutputKey==`WebSocketWssEndpoint`].OutputValue' \
    --output text \
    --region $REGION)
SNS_TOPIC=$(aws cloudformation describe-stacks \
    --stack-name alerta-realtime \
    --query 'Stacks[0].Outputs[?OutputKey==`IncidentAlertsTopicArn`].OutputValue' \
    --output text \
    --region $REGION)

echo "✅ Tiempo real desplegado"
echo "   WebSocket: $WS_ENDPOINT"
echo "   SNS Topic: $SNS_TOPIC"
cd ../..
echo ""

echo -e "${YELLOW}Paso 3: Desplegar backend de incidentes (REST API)${NC}"
cd services/incidents
sam build --use-container
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name alerta-incidents \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        LabRoleArn=$LAB_ROLE_ARN \
        IncidentsTableName=$INCIDENTS_TABLE \
    --resolve-s3 \
    --region $REGION \
    --no-confirm-changeset

API_URL=$(aws cloudformation describe-stacks \
    --stack-name alerta-incidents \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text \
    --region $REGION)

echo "✅ Backend de incidentes desplegado"
echo "   API URL: $API_URL"
cd ../..
echo ""

echo -e "${GREEN}✅ Deploy completado exitosamente!${NC}"
echo ""
echo "======================================"
echo "📋 RESUMEN DE RECURSOS DESPLEGADOS"
echo "======================================"
echo ""
echo "DynamoDB Table:"
echo "  - $INCIDENTS_TABLE (con Streams habilitado)"
echo ""
echo "WebSocket API (Tiempo Real):"
echo "  - Endpoint: $WS_ENDPOINT"
echo "  - Cliente demo: services/realtime/demo-client.html"
echo ""
echo "REST API (Incidentes):"
echo "  - Base URL: $API_URL"
echo "  - POST   $API_URL/incidents"
echo "  - GET    $API_URL/incidents"
echo "  - PATCH  $API_URL/incidents/{id}"
echo ""
echo "SNS Topic (Notificaciones):"
echo "  - ARN: $SNS_TOPIC"
echo "  - Suscribir email: aws sns subscribe --topic-arn $SNS_TOPIC --protocol email --notification-endpoint tu-email@utec.edu.pe"
echo ""
echo "======================================"
echo "🧪 PRUEBAS RÁPIDAS"
echo "======================================"
echo ""
echo "1. Abrir cliente WebSocket:"
echo "   cd services/realtime && python3 -m http.server 8080"
echo "   Luego navega a: http://localhost:8080/demo-client.html"
echo ""
echo "2. Crear incidente de prueba:"
echo "   aws dynamodb put-item --table-name $INCIDENTS_TABLE --item '{"
echo "     \"id\": {\"S\": \"test-001\"},"
echo "     \"status\": {\"S\": \"pending\"},"
echo "     \"urgencia\": {\"S\": \"alta\"},"
echo "     \"ubicacion\": {\"S\": \"Lab Demo\"},"
echo "     \"titulo\": {\"S\": \"Prueba del sistema\"}"
echo "   }'"
echo ""
echo "3. Ver el evento en tiempo real en el cliente WebSocket ✨"
echo ""
echo "======================================"
echo "Para más información:"
echo "  - README.md"
echo "  - docs/arquitectura-completa.md"
echo "  - services/incidents/README.md"
echo "  - services/realtime/README.md"
echo "======================================"
