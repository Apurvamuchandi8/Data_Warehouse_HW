WITH filtered_session_timestamp AS (
    SELECT
        sessionId,
        ts
    FROM {{ source('raw_data', 'session_timestamp') }}
    WHERE sessionId IS NOT NULL
)
SELECT * FROM filtered_session_timestamp
