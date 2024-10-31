WITH filtered_user_sessions AS (
    SELECT
        userId,
        sessionId,
        channel
    FROM {{ source('raw_data', 'user_session_channel') }}
    WHERE sessionId IS NOT NULL
)
SELECT * FROM filtered_user_sessions