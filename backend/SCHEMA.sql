CREATE SCHEMA "public";
CREATE SCHEMA "neon_auth";
CREATE TABLE "alerts" (
	"alert_id" serial PRIMARY KEY,
	"hospital_id" varchar(50) NOT NULL,
	"medicine_id" varchar(50),
	"alert_type" varchar(50) NOT NULL,
	"alert_message" text NOT NULL,
	"alert_status" varchar(50) NOT NULL,
	"created_at" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"resolved_at" timestamp
);
CREATE TABLE "hospital_predictions" (
	"hospital_id" varchar(50),
	"medicine_id" varchar(50),
	"medicine_name" varchar(255) NOT NULL,
	"x1_amc" numeric(12, 4),
	"x2_prescriptions" integer,
	"x3_cdpr" numeric(10, 4),
	"x4_cv" numeric(10, 4),
	"lead_time" integer,
	"safety_stock" integer,
	"reorder_stock" integer,
	"max_stock" integer,
	"daily_holding_charges" numeric(12, 4),
	CONSTRAINT "hospital_predictions_pkey" PRIMARY KEY("hospital_id","medicine_id")
);
CREATE TABLE "hospital_stock" (
	"hospital_id" varchar(50),
	"medicine_id" varchar(50),
	"medicine_name" varchar(255) NOT NULL,
	"medicine_expiry" date NOT NULL,
	"medicine_quantity" integer NOT NULL,
	CONSTRAINT "hospital_stock_pkey" PRIMARY KEY("hospital_id","medicine_id"),
	CONSTRAINT "hospital_stock_medicine_quantity_check" CHECK (CHECK ((medicine_quantity >= 0)))
);
CREATE TABLE "hospital_usage" (
	"hospital_id" varchar(50),
	"usage_date" date DEFAULT CURRENT_DATE,
	"medicine_id" varchar(50),
	"medicine_name" varchar(255) NOT NULL,
	"usage_amount" integer NOT NULL,
	CONSTRAINT "hospital_usage_pkey" PRIMARY KEY("hospital_id","medicine_id","usage_date"),
	CONSTRAINT "hospital_usage_usage_amount_check" CHECK (CHECK ((usage_amount >= 0)))
);
CREATE TABLE "medicine_info" (
	"hospital_id" varchar(50),
	"medicine_id" varchar(50),
	"medicine_name" varchar(255) NOT NULL,
	"medicine_price" numeric(12, 2) NOT NULL,
	"cold_storage" boolean NOT NULL,
	"abc_category" char(1),
	"ved_category" char(1),
	"salt_composition" text,
	"pack_size" varchar(50),
	CONSTRAINT "medicine_info_pkey" PRIMARY KEY("hospital_id","medicine_id")
);
CREATE TABLE "orders" (
	"order_id" serial PRIMARY KEY,
	"hospital_id" varchar(50) NOT NULL,
	"medicine_id" varchar(50) NOT NULL,
	"medicine_name" varchar(255) NOT NULL,
	"medicine_quantity_predicted" integer NOT NULL,
	"recieved_quantity" integer,
	"expected_delivery_date" date NOT NULL,
	"actual_delivery_date" date,
	"order_status" varchar(50) NOT NULL,
	"medicine_price" numeric(12, 2) NOT NULL,
	"created_at" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT "orders_medicine_quantity_predicted_check" CHECK (CHECK ((medicine_quantity_predicted >= 0))),
	CONSTRAINT "orders_recieved_quantity_check" CHECK (CHECK ((recieved_quantity >= 0)))
);
CREATE TABLE "organizations" (
	"organization_id" varchar(50) PRIMARY KEY,
	"organization_name" varchar(255) NOT NULL,
	"organization_type" varchar(50) NOT NULL,
	"created_at" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"uploaded_files" boolean,
	"uploaded_time" timestamp
);
CREATE TABLE "users" (
	"user_id" varchar(50) PRIMARY KEY,
	"hospital_id" varchar(50) NOT NULL,
	"user_name" varchar(255) NOT NULL,
	"user_email" varchar(255) NOT NULL CONSTRAINT "users_user_email_key" UNIQUE,
	"user_role" varchar(50) NOT NULL,
	"is_active" boolean DEFAULT true NOT NULL,
	"created_at" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"hashed_password" varchar(255) DEFAULT 'temp_hash' NOT NULL
);
CREATE TABLE "neon_auth"."account" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"accountId" text NOT NULL,
	"providerId" text NOT NULL,
	"userId" uuid NOT NULL,
	"accessToken" text,
	"refreshToken" text,
	"idToken" text,
	"accessTokenExpiresAt" timestamp with time zone,
	"refreshTokenExpiresAt" timestamp with time zone,
	"scope" text,
	"password" text,
	"createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updatedAt" timestamp with time zone NOT NULL
);
CREATE TABLE "neon_auth"."invitation" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"organizationId" uuid NOT NULL,
	"email" text NOT NULL,
	"role" text,
	"status" text NOT NULL,
	"expiresAt" timestamp with time zone NOT NULL,
	"createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"inviterId" uuid NOT NULL
);
CREATE TABLE "neon_auth"."jwks" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"publicKey" text NOT NULL,
	"privateKey" text NOT NULL,
	"createdAt" timestamp with time zone NOT NULL,
	"expiresAt" timestamp with time zone
);
CREATE TABLE "neon_auth"."member" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"organizationId" uuid NOT NULL,
	"userId" uuid NOT NULL,
	"role" text NOT NULL,
	"createdAt" timestamp with time zone NOT NULL
);
CREATE TABLE "neon_auth"."organization" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"name" text NOT NULL,
	"slug" text NOT NULL CONSTRAINT "organization_slug_key" UNIQUE,
	"logo" text,
	"createdAt" timestamp with time zone NOT NULL,
	"metadata" text
);
CREATE TABLE "neon_auth"."project_config" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"name" text NOT NULL,
	"endpoint_id" text NOT NULL CONSTRAINT "project_config_endpoint_id_key" UNIQUE,
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"trusted_origins" jsonb NOT NULL,
	"social_providers" jsonb NOT NULL,
	"email_provider" jsonb,
	"email_and_password" jsonb,
	"allow_localhost" boolean NOT NULL
);
CREATE TABLE "neon_auth"."session" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"expiresAt" timestamp with time zone NOT NULL,
	"token" text NOT NULL CONSTRAINT "session_token_key" UNIQUE,
	"createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updatedAt" timestamp with time zone NOT NULL,
	"ipAddress" text,
	"userAgent" text,
	"userId" uuid NOT NULL,
	"impersonatedBy" text,
	"activeOrganizationId" text
);
CREATE TABLE "neon_auth"."user" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"name" text NOT NULL,
	"email" text NOT NULL CONSTRAINT "user_email_key" UNIQUE,
	"emailVerified" boolean NOT NULL,
	"image" text,
	"createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updatedAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"role" text,
	"banned" boolean,
	"banReason" text,
	"banExpires" timestamp with time zone
);
CREATE TABLE "neon_auth"."verification" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"identifier" text NOT NULL,
	"value" text NOT NULL,
	"expiresAt" timestamp with time zone NOT NULL,
	"createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updatedAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
ALTER TABLE "alerts" ADD CONSTRAINT "fk_alert_hospital" FOREIGN KEY ("hospital_id") REFERENCES "organizations"("organization_id");
ALTER TABLE "alerts" ADD CONSTRAINT "fk_alert_medicine" FOREIGN KEY ("hospital_id","medicine_id") REFERENCES "medicine_info"("hospital_id","medicine_id");
ALTER TABLE "hospital_predictions" ADD CONSTRAINT "fk_prediction_medicine" FOREIGN KEY ("hospital_id","medicine_id") REFERENCES "medicine_info"("hospital_id","medicine_id");
ALTER TABLE "hospital_stock" ADD CONSTRAINT "fk_stock_medicine" FOREIGN KEY ("hospital_id","medicine_id") REFERENCES "medicine_info"("hospital_id","medicine_id");
ALTER TABLE "hospital_usage" ADD CONSTRAINT "fk_usage_medicine" FOREIGN KEY ("hospital_id","medicine_id") REFERENCES "medicine_info"("hospital_id","medicine_id");
ALTER TABLE "medicine_info" ADD CONSTRAINT "fk_medicine_hospital" FOREIGN KEY ("hospital_id") REFERENCES "organizations"("organization_id");
ALTER TABLE "orders" ADD CONSTRAINT "fk_orders_hospital" FOREIGN KEY ("hospital_id") REFERENCES "organizations"("organization_id");
ALTER TABLE "orders" ADD CONSTRAINT "fk_orders_medicine" FOREIGN KEY ("hospital_id","medicine_id") REFERENCES "medicine_info"("hospital_id","medicine_id");
ALTER TABLE "users" ADD CONSTRAINT "fk_user_hospital" FOREIGN KEY ("hospital_id") REFERENCES "organizations"("organization_id");
ALTER TABLE "neon_auth"."account" ADD CONSTRAINT "account_userId_fkey" FOREIGN KEY ("userId") REFERENCES "neon_auth"."user"("id") ON DELETE CASCADE;
ALTER TABLE "neon_auth"."invitation" ADD CONSTRAINT "invitation_inviterId_fkey" FOREIGN KEY ("inviterId") REFERENCES "neon_auth"."user"("id") ON DELETE CASCADE;
ALTER TABLE "neon_auth"."invitation" ADD CONSTRAINT "invitation_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES "neon_auth"."organization"("id") ON DELETE CASCADE;
ALTER TABLE "neon_auth"."member" ADD CONSTRAINT "member_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES "neon_auth"."organization"("id") ON DELETE CASCADE;
ALTER TABLE "neon_auth"."member" ADD CONSTRAINT "member_userId_fkey" FOREIGN KEY ("userId") REFERENCES "neon_auth"."user"("id") ON DELETE CASCADE;
ALTER TABLE "neon_auth"."session" ADD CONSTRAINT "session_userId_fkey" FOREIGN KEY ("userId") REFERENCES "neon_auth"."user"("id") ON DELETE CASCADE;
CREATE UNIQUE INDEX "alerts_pkey" ON "alerts" ("alert_id");
CREATE UNIQUE INDEX "hospital_predictions_pkey" ON "hospital_predictions" ("hospital_id","medicine_id");
CREATE UNIQUE INDEX "hospital_stock_pkey" ON "hospital_stock" ("hospital_id","medicine_id");
CREATE UNIQUE INDEX "hospital_usage_pkey" ON "hospital_usage" ("hospital_id","medicine_id","usage_date");
CREATE UNIQUE INDEX "medicine_info_pkey" ON "medicine_info" ("hospital_id","medicine_id");
CREATE UNIQUE INDEX "orders_pkey" ON "orders" ("order_id");
CREATE UNIQUE INDEX "organizations_pkey" ON "organizations" ("organization_id");
CREATE UNIQUE INDEX "users_pkey" ON "users" ("user_id");
CREATE UNIQUE INDEX "users_user_email_key" ON "users" ("user_email");
CREATE UNIQUE INDEX "account_pkey" ON "neon_auth"."account" ("id");
CREATE INDEX "account_userId_idx" ON "neon_auth"."account" ("userId");
CREATE INDEX "invitation_email_idx" ON "neon_auth"."invitation" ("email");
CREATE INDEX "invitation_organizationId_idx" ON "neon_auth"."invitation" ("organizationId");
CREATE UNIQUE INDEX "invitation_pkey" ON "neon_auth"."invitation" ("id");
CREATE UNIQUE INDEX "jwks_pkey" ON "neon_auth"."jwks" ("id");
CREATE INDEX "member_organizationId_idx" ON "neon_auth"."member" ("organizationId");
CREATE UNIQUE INDEX "member_pkey" ON "neon_auth"."member" ("id");
CREATE INDEX "member_userId_idx" ON "neon_auth"."member" ("userId");
CREATE UNIQUE INDEX "organization_pkey" ON "neon_auth"."organization" ("id");
CREATE UNIQUE INDEX "organization_slug_key" ON "neon_auth"."organization" ("slug");
CREATE UNIQUE INDEX "organization_slug_uidx" ON "neon_auth"."organization" ("slug");
CREATE UNIQUE INDEX "project_config_endpoint_id_key" ON "neon_auth"."project_config" ("endpoint_id");
CREATE UNIQUE INDEX "project_config_pkey" ON "neon_auth"."project_config" ("id");
CREATE UNIQUE INDEX "session_pkey" ON "neon_auth"."session" ("id");
CREATE UNIQUE INDEX "session_token_key" ON "neon_auth"."session" ("token");
CREATE INDEX "session_userId_idx" ON "neon_auth"."session" ("userId");
CREATE UNIQUE INDEX "user_email_key" ON "neon_auth"."user" ("email");
CREATE UNIQUE INDEX "user_pkey" ON "neon_auth"."user" ("id");
CREATE INDEX "verification_identifier_idx" ON "neon_auth"."verification" ("identifier");
CREATE UNIQUE INDEX "verification_pkey" ON "neon_auth"."verification" ("id");