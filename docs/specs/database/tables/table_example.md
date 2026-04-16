# Table: accounts

## Overview
- **Purpose:** アカウント情報マスタ
- **Module:** Authentication
- **Record Volume:** [Expected: Low/Medium/High]

## Schema Definition

| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | BIGINT | NO | AUTO_INCREMENT | ID | ID |
| role_id | BIGINT | NO | - | 権限ID | 権限ID |
| store_id | BIGINT | YES | - | 店舗ID | 店舗ID |
| email | VARCHAR(50) | NO | - | メールアドレス | メールアドレス |
| password | VARCHAR(255) | NO | - | パスワード | パスワード |
| created_at | DATETIME | NO | - | 作成日時 | 作成日時 |
| updated_at | DATETIME | YES | - | 更新日時 | 更新日時 |
| deleted_at | DATETIME | YES | - | 削除日時 | 削除日時 |

## Relationships

### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| role_id | roles.id | - |
| store_id | stores.id | - |

### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| - | - | - |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| PRIMARY | id | PRIMARY | Primary key |

## Laravel Migration

```php
Schema::create('accounts', function (Blueprint $table) {
    $table->id();
    $table->foreignId('role_id')->constrained('roles');
    $table->foreignId('store_id')->nullable()->constrained('stores');
    $table->string('email', 50);
    $table->string('password', 255);
    $table->timestamp('created_at')->useCurrent();
    $table->timestamp('updated_at')->useCurrent()->useCurrentOnUpdate();
    $table->softDeletes();
});
```