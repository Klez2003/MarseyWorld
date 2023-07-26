--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3 (Ubuntu 15.3-1.pgdg22.04+1)
-- Dumped by pg_dump version 15.3 (Ubuntu 15.3-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- Name: hypopg; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS hypopg WITH SCHEMA public;


--
-- Name: EXTENSION hypopg; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION hypopg IS 'Hypothetical indexes for PostgreSQL';


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: casino_game_currency; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.casino_game_currency AS ENUM (
    'coins',
    'marseybux'
);


--
-- Name: casino_game_kind; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.casino_game_kind AS ENUM (
    'blackjack',
    'slots',
    'roulette'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(30) NOT NULL,
    email character varying(255),
    passhash character varying(255) NOT NULL,
    created_utc integer NOT NULL,
    admin_level integer DEFAULT 0 NOT NULL,
    over_18 boolean DEFAULT false NOT NULL,
    is_activated boolean DEFAULT false NOT NULL,
    bio character varying(5000),
    bio_html character varying(20000),
    referred_by integer,
    is_banned integer,
    ban_reason character varying(256),
    login_nonce integer DEFAULT 0 NOT NULL,
    reserved character varying(256),
    mfa_secret character varying(32),
    is_private boolean DEFAULT false NOT NULL,
    unban_utc integer DEFAULT 0 NOT NULL,
    custom_filter_list character varying(1000) DEFAULT ''::character varying,
    stored_subscriber_count integer DEFAULT 0 NOT NULL,
    original_username character varying(30),
    customtitle character varying(1000),
    defaultsorting character varying(15) NOT NULL,
    defaulttime character varying(5) NOT NULL,
    namecolor character varying(6) NOT NULL,
    titlecolor character varying(6) NOT NULL,
    profileurl character varying(65),
    bannerurl character varying(65),
    newtab boolean DEFAULT false NOT NULL,
    flairchanged integer,
    defaultsortingcomments character varying(15) NOT NULL,
    theme character varying(15) NOT NULL,
    song character varying(50),
    slurreplacer integer DEFAULT 1 NOT NULL,
    shadowbanned integer,
    newtabexternal boolean DEFAULT true NOT NULL,
    customtitleplain character varying(100),
    themecolor character varying(6) NOT NULL,
    css character varying(10000),
    profilecss character varying(10000),
    coins integer DEFAULT 0 NOT NULL,
    chud integer DEFAULT 0 NOT NULL,
    post_count integer DEFAULT 0 NOT NULL,
    comment_count integer DEFAULT 0 NOT NULL,
    highres character varying(60),
    patron integer DEFAULT 0 NOT NULL,
    controversial boolean DEFAULT false NOT NULL,
    background character varying(167),
    verified character varying(100),
    received_award_count integer DEFAULT 0 NOT NULL,
    nitter boolean,
    truescore integer DEFAULT 0 NOT NULL,
    frontsize integer DEFAULT 25 NOT NULL,
    coins_spent integer DEFAULT 0 NOT NULL,
    marseybux integer DEFAULT 0 NOT NULL,
    verifiedcolor character varying(6),
    marseyawarded integer,
    sig character varying(200),
    sig_html character varying(1000),
    friends character varying(5000),
    friends_html character varying(20000),
    sigs_disabled boolean,
    enemies character varying(5000),
    enemies_html character varying(20000),
    fp character varying(21),
    longpost integer,
    bird integer,
    lootboxes_bought integer DEFAULT 0 NOT NULL,
    progressivestack integer,
    patron_utc integer DEFAULT 0 NOT NULL,
    rehab integer,
    house character varying(16),
    deflector integer,
    reddit character varying(15) NOT NULL,
    currently_held_lottery_tickets integer DEFAULT 0 NOT NULL,
    total_held_lottery_tickets integer DEFAULT 0 NOT NULL,
    total_lottery_winnings integer DEFAULT 0 NOT NULL,
    last_active integer DEFAULT 0 NOT NULL,
    last_viewed_post_notifs integer NOT NULL,
    pronouns character varying(15) NOT NULL,
    last_viewed_log_notifs integer NOT NULL,
    imginn boolean,
    earlylife integer,
    bite integer,
    old_house character varying(16),
    owoify integer,
    marsify integer,
    is_muted boolean DEFAULT false NOT NULL,
    coins_spent_on_hats integer DEFAULT 0 NOT NULL,
    rainbow integer,
    spider integer,
    profanityreplacer integer DEFAULT 1 NOT NULL,
    last_viewed_reddit_notifs integer NOT NULL,
    profile_background character varying(167),
    event_music boolean,
    chudded_by integer,
    blacklisted_by integer,
    hidevotedon boolean DEFAULT false NOT NULL,
    chud_phrase character varying(35),
    prelock_username character varying(30),
    namechanged integer,
    queen integer,
    sharpen integer
);


--
-- Name: lifetimedonated(public.users); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.lifetimedonated(public.users) RETURNS integer
    LANGUAGE sql IMMUTABLE STRICT
    AS $_$
      select sum(amount)
      from transactions
      where transactions.email = $1.email
      $_$;


--
-- Name: alts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alts (
    user1 integer NOT NULL,
    user2 integer NOT NULL,
    is_manual boolean DEFAULT false NOT NULL,
    created_utc integer,
    CONSTRAINT alts_cant_be_equal CHECK ((user1 <> user2))
);


--
-- Name: award_relationships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.award_relationships (
    id integer NOT NULL,
    user_id integer NOT NULL,
    post_id integer,
    comment_id integer,
    kind character varying(20) NOT NULL,
    awarded_utc integer,
    created_utc integer,
    price_paid integer DEFAULT 0 NOT NULL
);


--
-- Name: award_relationships_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.award_relationships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: award_relationships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.award_relationships_id_seq OWNED BY public.award_relationships.id;


--
-- Name: badge_defs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.badge_defs (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(200),
    created_utc integer
);


--
-- Name: badge_defs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.badge_defs_id_seq
    AS integer
    START WITH 106
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: badge_defs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.badge_defs_id_seq OWNED BY public.badge_defs.id;


--
-- Name: badges; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.badges (
    badge_id integer NOT NULL,
    user_id integer NOT NULL,
    description character varying(256),
    url character varying(256),
    created_utc integer NOT NULL
);


--
-- Name: banneddomains; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.banneddomains (
    domain character varying(100) NOT NULL,
    reason character varying(100) NOT NULL,
    created_utc integer
);


--
-- Name: casino_games; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.casino_games (
    id integer NOT NULL,
    user_id integer NOT NULL,
    created_utc integer NOT NULL,
    active boolean DEFAULT true NOT NULL,
    currency public.casino_game_currency NOT NULL,
    wager integer NOT NULL,
    winnings integer NOT NULL,
    kind public.casino_game_kind NOT NULL,
    game_state jsonb NOT NULL
);


--
-- Name: casino_games_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.casino_games_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: casino_games_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.casino_games_id_seq OWNED BY public.casino_games.id;


--
-- Name: client_auths; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client_auths (
    user_id integer NOT NULL,
    oauth_client integer NOT NULL,
    access_token character(128) NOT NULL,
    created_utc integer
);


--
-- Name: comment_option_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comment_option_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comment_option_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comment_option_votes (
    option_id integer NOT NULL,
    user_id integer NOT NULL,
    created_utc integer NOT NULL,
    comment_id integer
);


--
-- Name: comment_options; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comment_options (
    id integer DEFAULT nextval('public.comment_option_id_seq'::regclass) NOT NULL,
    parent_id integer NOT NULL,
    body_html character varying(500) NOT NULL,
    exclusive integer NOT NULL,
    created_utc integer
);


--
-- Name: comment_save_relationship; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comment_save_relationship (
    user_id integer NOT NULL,
    comment_id integer NOT NULL,
    created_utc integer
);


--
-- Name: commentreports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.commentreports (
    user_id integer NOT NULL,
    comment_id integer NOT NULL,
    reason character varying(350),
    created_utc integer NOT NULL
);


--
-- Name: comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comments (
    id integer NOT NULL,
    author_id integer NOT NULL,
    created_utc integer NOT NULL,
    parent_post integer,
    is_banned boolean DEFAULT false NOT NULL,
    distinguish_level integer DEFAULT 0 NOT NULL,
    edited_utc integer DEFAULT 0 NOT NULL,
    deleted_utc integer DEFAULT 0 NOT NULL,
    is_approved integer,
    level integer DEFAULT 0 NOT NULL,
    parent_comment_id integer,
    over_18 boolean DEFAULT false NOT NULL,
    upvotes integer DEFAULT 1 NOT NULL,
    downvotes integer DEFAULT 0 NOT NULL,
    is_bot boolean DEFAULT false NOT NULL,
    app_id integer,
    sentto integer,
    bannedfor character varying(50),
    stickied character varying(40),
    body character varying(10000),
    body_html character varying(40000),
    ban_reason character varying(25),
    realupvotes integer DEFAULT 1 NOT NULL,
    top_comment_id integer,
    stickied_utc integer,
    ghost boolean DEFAULT false NOT NULL,
    slots_result character varying(36),
    blackjack_result character varying(860),
    treasure_amount character varying(10),
    body_ts tsvector GENERATED ALWAYS AS (to_tsvector('english'::regconfig, (body)::text)) STORED,
    casino_game_id integer,
    chuddedfor character varying(50),
    stickied_child_id integer,
    wall_user_id integer,
    chudded boolean,
    ping_cost integer
);


--
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;


--
-- Name: commentvotes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.commentvotes (
    comment_id integer NOT NULL,
    vote_type integer NOT NULL,
    user_id integer NOT NULL,
    "real" boolean DEFAULT true NOT NULL,
    created_utc integer NOT NULL,
    coins smallint DEFAULT 1 NOT NULL
);


--
-- Name: emojis; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.emojis (
    name character varying(30) NOT NULL,
    author_id integer NOT NULL,
    tags character varying(200) NOT NULL,
    count integer DEFAULT 0 NOT NULL,
    submitter_id integer,
    created_utc integer,
    kind character varying(15) NOT NULL
);


--
-- Name: exiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.exiles (
    user_id integer NOT NULL,
    sub character varying(25) NOT NULL,
    exiler_id integer NOT NULL,
    created_utc integer
);


--
-- Name: follows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.follows (
    user_id integer NOT NULL,
    target_id integer NOT NULL,
    created_utc integer NOT NULL
);


--
-- Name: group_memberships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_memberships (
    user_id integer NOT NULL,
    group_name character varying(25) NOT NULL,
    created_utc integer NOT NULL,
    approved_utc integer
);


--
-- Name: groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.groups (
    name character varying(25) NOT NULL,
    created_utc integer NOT NULL
);


--
-- Name: hat_defs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hat_defs (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(300) NOT NULL,
    author_id integer NOT NULL,
    price integer NOT NULL,
    submitter_id integer,
    created_utc integer NOT NULL
);


--
-- Name: hat_defs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hat_defs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hat_defs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hat_defs_id_seq OWNED BY public.hat_defs.id;


--
-- Name: hats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hats (
    hat_id integer NOT NULL,
    user_id integer NOT NULL,
    equipped boolean,
    created_utc integer
);


--
-- Name: lotteries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lotteries (
    id integer NOT NULL,
    is_active boolean DEFAULT false NOT NULL,
    ends_at integer DEFAULT 0 NOT NULL,
    prize integer DEFAULT 0 NOT NULL,
    tickets_sold integer DEFAULT 0 NOT NULL,
    winner_id integer,
    created_utc integer
);


--
-- Name: lotteries_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.lotteries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: lotteries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.lotteries_id_seq OWNED BY public.lotteries.id;


--
-- Name: media; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.media (
    kind character varying(5) NOT NULL,
    filename character varying(200) NOT NULL,
    user_id integer NOT NULL,
    created_utc integer NOT NULL,
    size integer NOT NULL
);


--
-- Name: modactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.modactions (
    id integer NOT NULL,
    user_id integer,
    target_user_id integer,
    target_post_id integer,
    target_comment_id integer,
    created_utc integer NOT NULL,
    kind character varying(33) DEFAULT NULL::character varying,
    _note character varying(2019) DEFAULT NULL::character varying
);


--
-- Name: modactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.modactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: modactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.modactions_id_seq OWNED BY public.modactions.id;


--
-- Name: mods; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mods (
    user_id integer NOT NULL,
    sub character varying(25) NOT NULL,
    created_utc integer NOT NULL
);


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    user_id integer NOT NULL,
    comment_id integer NOT NULL,
    read boolean NOT NULL,
    created_utc integer NOT NULL
);


--
-- Name: oauth_apps; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.oauth_apps (
    id integer NOT NULL,
    client_id character(64),
    app_name character varying(50) NOT NULL,
    redirect_uri character varying(4096) NOT NULL,
    author_id integer NOT NULL,
    description character varying(256) NOT NULL,
    created_utc integer
);


--
-- Name: oauth_apps_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.oauth_apps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: oauth_apps_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.oauth_apps_id_seq OWNED BY public.oauth_apps.id;


--
-- Name: orgies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orgies (
    id integer NOT NULL,
    type integer NOT NULL,
    data character varying(200) NOT NULL,
    title character varying(1000) NOT NULL
);


--
-- Name: pgbench_accounts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pgbench_accounts (
    aid integer NOT NULL,
    bid integer,
    abalance integer,
    filler character(84)
)
WITH (fillfactor='100');


--
-- Name: pgbench_branches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pgbench_branches (
    bid integer NOT NULL,
    bbalance integer,
    filler character(88)
)
WITH (fillfactor='100');


--
-- Name: pgbench_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pgbench_history (
    tid integer,
    bid integer,
    aid integer,
    delta integer,
    mtime timestamp without time zone,
    filler character(22)
);


--
-- Name: pgbench_tellers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pgbench_tellers (
    tid integer NOT NULL,
    bid integer,
    tbalance integer,
    filler character(84)
)
WITH (fillfactor='100');


--
-- Name: posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    author_id integer NOT NULL,
    created_utc integer NOT NULL,
    is_banned boolean DEFAULT false NOT NULL,
    over_18 boolean DEFAULT false NOT NULL,
    distinguish_level integer DEFAULT 0 NOT NULL,
    deleted_utc integer DEFAULT 0 NOT NULL,
    is_approved integer,
    edited_utc integer DEFAULT 0 NOT NULL,
    is_pinned boolean DEFAULT false NOT NULL,
    upvotes integer DEFAULT 1 NOT NULL,
    downvotes integer DEFAULT 0 NOT NULL,
    app_id integer,
    thumburl character varying(200),
    private boolean DEFAULT false NOT NULL,
    views integer DEFAULT 0 NOT NULL,
    is_bot boolean DEFAULT false NOT NULL,
    bannedfor character varying(50),
    comment_count integer DEFAULT 0 NOT NULL,
    stickied character varying(40),
    title character varying(500) NOT NULL,
    url character varying(2083),
    body character varying(100000),
    body_html character varying(200000),
    embed character varying(1500),
    ban_reason character varying(25),
    title_html character varying(1500) NOT NULL,
    realupvotes integer,
    flair character varying(350),
    stickied_utc integer,
    ghost boolean DEFAULT false NOT NULL,
    sub character varying(25),
    new boolean,
    hole_pinned character varying(30),
    notify boolean NOT NULL,
    chuddedfor character varying(50),
    posterurl character varying(200),
    chudded boolean,
    ping_cost integer,
    bump_utc integer NOT NULL
);


--
-- Name: post_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.post_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: post_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.post_id_seq OWNED BY public.posts.id;


--
-- Name: post_option_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.post_option_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: post_option_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_option_votes (
    option_id integer NOT NULL,
    user_id integer NOT NULL,
    created_utc integer NOT NULL,
    post_id integer
);


--
-- Name: post_options; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_options (
    id integer DEFAULT nextval('public.post_option_id_seq'::regclass) NOT NULL,
    parent_id integer NOT NULL,
    body_html character varying(500) NOT NULL,
    exclusive integer NOT NULL,
    created_utc integer
);


--
-- Name: push_subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.push_subscriptions (
    user_id integer NOT NULL,
    subscription_json character varying(600) NOT NULL,
    created_utc integer NOT NULL
);


--
-- Name: reports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reports (
    user_id integer NOT NULL,
    post_id integer NOT NULL,
    reason character varying(350),
    created_utc integer NOT NULL
);


--
-- Name: save_relationship; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.save_relationship (
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    created_utc integer
);


--
-- Name: sub_blocks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sub_blocks (
    user_id integer NOT NULL,
    sub character varying(25) NOT NULL,
    created_utc integer
);


--
-- Name: sub_joins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sub_joins (
    user_id integer NOT NULL,
    sub character varying(25) NOT NULL,
    created_utc integer
);


--
-- Name: sub_subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sub_subscriptions (
    user_id integer NOT NULL,
    sub character varying(25) NOT NULL,
    created_utc integer
);


--
-- Name: subactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subactions (
    id integer NOT NULL,
    sub character varying(25) NOT NULL,
    user_id integer,
    target_user_id integer,
    target_post_id integer,
    target_comment_id integer,
    created_utc integer NOT NULL,
    kind character varying(32) DEFAULT NULL::character varying,
    _note character varying(2019) DEFAULT NULL::character varying
);


--
-- Name: subactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.subactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: subactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.subactions_id_seq OWNED BY public.subactions.id;


--
-- Name: subs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subs (
    name character varying(25) NOT NULL,
    sidebar character varying(10000),
    sidebar_html character varying(20000),
    sidebarurl character varying(60),
    bannerurls character varying(60)[] DEFAULT '{}'::character varying[] NOT NULL,
    css character varying(6000),
    stealth boolean,
    marseyurl character varying(60),
    created_utc integer
);


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subscriptions (
    user_id integer NOT NULL,
    post_id integer NOT NULL,
    created_utc integer
);


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transactions (
    id character varying(64) NOT NULL,
    created_utc integer NOT NULL,
    type character varying(12) NOT NULL,
    amount integer NOT NULL,
    email character varying(255) NOT NULL,
    claimed boolean
);


--
-- Name: userblocks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.userblocks (
    user_id integer NOT NULL,
    target_id integer NOT NULL,
    created_utc integer
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: viewers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.viewers (
    user_id integer NOT NULL,
    viewer_id integer NOT NULL,
    last_view_utc integer NOT NULL,
    created_utc integer
);


--
-- Name: votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.votes (
    user_id integer NOT NULL,
    post_id integer NOT NULL,
    vote_type integer NOT NULL,
    "real" boolean DEFAULT true NOT NULL,
    created_utc integer NOT NULL,
    coins smallint DEFAULT 1 NOT NULL
);


--
-- Name: award_relationships id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships ALTER COLUMN id SET DEFAULT nextval('public.award_relationships_id_seq'::regclass);


--
-- Name: badge_defs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badge_defs ALTER COLUMN id SET DEFAULT nextval('public.badge_defs_id_seq'::regclass);


--
-- Name: casino_games id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.casino_games ALTER COLUMN id SET DEFAULT nextval('public.casino_games_id_seq'::regclass);


--
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);


--
-- Name: hat_defs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hat_defs ALTER COLUMN id SET DEFAULT nextval('public.hat_defs_id_seq'::regclass);


--
-- Name: lotteries id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lotteries ALTER COLUMN id SET DEFAULT nextval('public.lotteries_id_seq'::regclass);


--
-- Name: modactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modactions ALTER COLUMN id SET DEFAULT nextval('public.modactions_id_seq'::regclass);


--
-- Name: oauth_apps id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oauth_apps ALTER COLUMN id SET DEFAULT nextval('public.oauth_apps_id_seq'::regclass);


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.post_id_seq'::regclass);


--
-- Name: subactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subactions ALTER COLUMN id SET DEFAULT nextval('public.subactions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: alts alts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alts
    ADD CONSTRAINT alts_pkey PRIMARY KEY (user1, user2);


--
-- Name: award_relationships award_constraint; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_constraint UNIQUE (user_id, post_id, comment_id);


--
-- Name: award_relationships award_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_relationships_pkey PRIMARY KEY (id);


--
-- Name: badge_defs badge_def_name_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badge_defs
    ADD CONSTRAINT badge_def_name_unique UNIQUE (name);


--
-- Name: badge_defs badge_defs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badge_defs
    ADD CONSTRAINT badge_defs_pkey PRIMARY KEY (id);


--
-- Name: badges badges_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badges
    ADD CONSTRAINT badges_pkey PRIMARY KEY (user_id, badge_id);


--
-- Name: casino_games casino_games_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.casino_games
    ADD CONSTRAINT casino_games_pkey PRIMARY KEY (id);


--
-- Name: client_auths client_auths_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_auths
    ADD CONSTRAINT client_auths_pkey PRIMARY KEY (user_id, oauth_client);


--
-- Name: comment_option_votes comment_option_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_option_votes
    ADD CONSTRAINT comment_option_votes_pkey PRIMARY KEY (option_id, user_id);


--
-- Name: comment_options comment_options_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_options
    ADD CONSTRAINT comment_options_pkey PRIMARY KEY (id);


--
-- Name: comment_save_relationship comment_save_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_save_relationship
    ADD CONSTRAINT comment_save_relationship_pkey PRIMARY KEY (user_id, comment_id);


--
-- Name: commentreports commentreports_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentreports
    ADD CONSTRAINT commentreports_pkey PRIMARY KEY (comment_id, user_id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: commentvotes commentvotes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentvotes
    ADD CONSTRAINT commentvotes_pkey PRIMARY KEY (comment_id, user_id);


--
-- Name: banneddomains domain_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.banneddomains
    ADD CONSTRAINT domain_pkey PRIMARY KEY (domain);


--
-- Name: emojis emoji_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emojis
    ADD CONSTRAINT emoji_pkey PRIMARY KEY (name);


--
-- Name: exiles exiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exiles
    ADD CONSTRAINT exiles_pkey PRIMARY KEY (user_id, sub);


--
-- Name: follows follows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follows
    ADD CONSTRAINT follows_pkey PRIMARY KEY (target_id, user_id);


--
-- Name: group_memberships group_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_pkey PRIMARY KEY (user_id, group_name);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (name);


--
-- Name: hat_defs hat_defs_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hat_defs
    ADD CONSTRAINT hat_defs_name_key UNIQUE (name);


--
-- Name: hat_defs hat_defs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hat_defs
    ADD CONSTRAINT hat_defs_pkey PRIMARY KEY (id);


--
-- Name: hats hats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hats
    ADD CONSTRAINT hats_pkey PRIMARY KEY (user_id, hat_id);


--
-- Name: lotteries lotteries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lotteries
    ADD CONSTRAINT lotteries_pkey PRIMARY KEY (id);


--
-- Name: media media_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media
    ADD CONSTRAINT media_pkey PRIMARY KEY (kind, filename);


--
-- Name: modactions modactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modactions
    ADD CONSTRAINT modactions_pkey PRIMARY KEY (id);


--
-- Name: mods mods_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mods
    ADD CONSTRAINT mods_pkey PRIMARY KEY (user_id, sub);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (user_id, comment_id);


--
-- Name: oauth_apps oauth_apps_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oauth_apps
    ADD CONSTRAINT oauth_apps_pkey PRIMARY KEY (id);


--
-- Name: users one_banner; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT one_banner UNIQUE (bannerurl);


--
-- Name: pgbench_accounts pgbench_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pgbench_accounts
    ADD CONSTRAINT pgbench_accounts_pkey PRIMARY KEY (aid);


--
-- Name: pgbench_branches pgbench_branches_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pgbench_branches
    ADD CONSTRAINT pgbench_branches_pkey PRIMARY KEY (bid);


--
-- Name: pgbench_tellers pgbench_tellers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pgbench_tellers
    ADD CONSTRAINT pgbench_tellers_pkey PRIMARY KEY (tid);


--
-- Name: post_options post_option_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_options
    ADD CONSTRAINT post_option_pkey PRIMARY KEY (id);


--
-- Name: post_option_votes post_option_vote_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_option_votes
    ADD CONSTRAINT post_option_vote_pkey PRIMARY KEY (option_id, user_id);


--
-- Name: posts post_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT post_pkey PRIMARY KEY (id);


--
-- Name: push_subscriptions push_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_subscriptions
    ADD CONSTRAINT push_subscriptions_pkey PRIMARY KEY (user_id, subscription_json);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (post_id, user_id);


--
-- Name: save_relationship save_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.save_relationship
    ADD CONSTRAINT save_relationship_pkey PRIMARY KEY (user_id, post_id);


--
-- Name: sub_blocks sub_blocks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_blocks
    ADD CONSTRAINT sub_blocks_pkey PRIMARY KEY (user_id, sub);


--
-- Name: sub_joins sub_joins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_joins
    ADD CONSTRAINT sub_joins_pkey PRIMARY KEY (user_id, sub);


--
-- Name: sub_subscriptions sub_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_subscriptions
    ADD CONSTRAINT sub_subscriptions_pkey PRIMARY KEY (user_id, sub);


--
-- Name: subactions subactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subactions
    ADD CONSTRAINT subactions_pkey PRIMARY KEY (id);


--
-- Name: subs subs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subs
    ADD CONSTRAINT subs_pkey PRIMARY KEY (name);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (post_id, user_id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: users uid_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT uid_unique UNIQUE (id);


--
-- Name: client_auths unique_access; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_auths
    ADD CONSTRAINT unique_access UNIQUE (access_token);


--
-- Name: oauth_apps unique_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oauth_apps
    ADD CONSTRAINT unique_id UNIQUE (client_id);


--
-- Name: userblocks userblocks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.userblocks
    ADD CONSTRAINT userblocks_pkey PRIMARY KEY (user_id, target_id);


--
-- Name: users users_original_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_original_username_key UNIQUE (original_username);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_prelock_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_prelock_username_key UNIQUE (prelock_username);


--
-- Name: users users_username_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_unique UNIQUE (username);


--
-- Name: viewers viewers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.viewers
    ADD CONSTRAINT viewers_pkey PRIMARY KEY (user_id, viewer_id);


--
-- Name: votes votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_pkey PRIMARY KEY (post_id, user_id);


--
-- Name: alts_unique_combination; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX alts_unique_combination ON public.alts USING btree (GREATEST(user1, user2), LEAST(user1, user2));


--
-- Name: alts_user2_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX alts_user2_idx ON public.alts USING btree (user2);


--
-- Name: award_comment_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX award_comment_idx ON public.award_relationships USING btree (comment_id);


--
-- Name: award_post_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX award_post_idx ON public.award_relationships USING btree (post_id);


--
-- Name: badges_badge_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX badges_badge_id_idx ON public.badges USING btree (badge_id);


--
-- Name: block_target_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX block_target_idx ON public.userblocks USING btree (target_id);


--
-- Name: casino_games_active_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX casino_games_active_user_id_idx ON public.casino_games USING btree (active, user_id);


--
-- Name: casino_games_created_utc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX casino_games_created_utc_idx ON public.casino_games USING btree (created_utc);


--
-- Name: casino_games_user_id_winnings_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX casino_games_user_id_winnings_idx ON public.casino_games USING btree (user_id, winnings);


--
-- Name: casino_games_winnings_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX casino_games_winnings_idx ON public.casino_games USING btree (winnings);


--
-- Name: comment_new_sort_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comment_new_sort_idx ON public.comments USING btree (is_banned, deleted_utc, created_utc DESC, over_18);


--
-- Name: comment_parent_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comment_parent_index ON public.comments USING btree (parent_comment_id);


--
-- Name: comment_post_id_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comment_post_id_index ON public.comments USING btree (parent_post);


--
-- Name: comments_author_id_created_utc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comments_author_id_created_utc_idx ON public.comments USING btree (author_id, created_utc);


--
-- Name: comments_author_id_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comments_author_id_id_idx ON public.comments USING btree (author_id, id);


--
-- Name: comments_body_ts_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comments_body_ts_idx ON public.comments USING gin (body_ts);


--
-- Name: comments_created_utc_asc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comments_created_utc_asc_idx ON public.comments USING btree (created_utc NULLS FIRST);


--
-- Name: comments_created_utc_desc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comments_created_utc_desc_idx ON public.comments USING btree (created_utc DESC);


--
-- Name: comments_deleted_utc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comments_deleted_utc_idx ON public.comments USING btree (deleted_utc);


--
-- Name: comments_top_comment_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comments_top_comment_id_idx ON public.comments USING btree (top_comment_id);


--
-- Name: commentvotes_commentid_userid_votetype_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX commentvotes_commentid_userid_votetype_idx ON public.commentvotes USING btree (comment_id, user_id, vote_type);


--
-- Name: commentvotes_comments_type_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX commentvotes_comments_type_index ON public.commentvotes USING btree (vote_type);


--
-- Name: commentvotes_user_id_vote_type_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX commentvotes_user_id_vote_type_idx ON public.commentvotes USING btree (user_id, vote_type) INCLUDE (comment_id);


--
-- Name: creport_user_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX creport_user_idx ON public.commentreports USING btree (user_id);


--
-- Name: emoji_kind; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX emoji_kind ON public.emojis USING btree (kind);


--
-- Name: emojis_idx2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX emojis_idx2 ON public.emojis USING btree (author_id);


--
-- Name: emojis_idx3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX emojis_idx3 ON public.emojis USING btree (count DESC);


--
-- Name: emojis_idx4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX emojis_idx4 ON public.emojis USING btree (submitter_id);


--
-- Name: fki_comment_approver_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_comment_approver_fkey ON public.comments USING btree (is_approved);


--
-- Name: fki_comment_save_relationship_comment_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_comment_save_relationship_comment_fkey ON public.comment_save_relationship USING btree (comment_id);


--
-- Name: fki_comment_sentto_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_comment_sentto_fkey ON public.comments USING btree (sentto);


--
-- Name: fki_exile_exiler_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_exile_exiler_fkey ON public.exiles USING btree (exiler_id);


--
-- Name: fki_exile_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_exile_sub_fkey ON public.exiles USING btree (sub);


--
-- Name: fki_mod_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_mod_sub_fkey ON public.mods USING btree (sub);


--
-- Name: fki_modactions_user_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_modactions_user_fkey ON public.modactions USING btree (target_user_id);


--
-- Name: fki_post_approver_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_post_approver_fkey ON public.posts USING btree (is_approved);


--
-- Name: fki_post_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_post_sub_fkey ON public.posts USING btree (sub);


--
-- Name: fki_save_relationship_post_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_save_relationship_post_fkey ON public.save_relationship USING btree (post_id);


--
-- Name: fki_sub_blocks_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_sub_blocks_sub_fkey ON public.sub_blocks USING btree (sub);


--
-- Name: fki_sub_joins_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_sub_joins_sub_fkey ON public.sub_joins USING btree (sub);


--
-- Name: fki_sub_subscriptions_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_sub_subscriptions_sub_fkey ON public.sub_subscriptions USING btree (sub);


--
-- Name: fki_subactions_user_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_subactions_user_fkey ON public.subactions USING btree (target_user_id);


--
-- Name: fki_user_chudded_by_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_user_chudded_by_fkey ON public.users USING btree (chudded_by);


--
-- Name: fki_user_is_banned_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_user_is_banned_fkey ON public.users USING btree (is_banned);


--
-- Name: fki_user_referrer_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_user_referrer_fkey ON public.users USING btree (referred_by);


--
-- Name: fki_user_shadowbanned_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_user_shadowbanned_fkey ON public.users USING btree (shadowbanned);


--
-- Name: fki_view_viewer_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_view_viewer_fkey ON public.viewers USING btree (viewer_id);


--
-- Name: fki_wall_user_id_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_wall_user_id_fkey ON public.comments USING btree (wall_user_id);


--
-- Name: follow_user_id_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX follow_user_id_index ON public.follows USING btree (user_id);


--
-- Name: hat_defs_submitter_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hat_defs_submitter_id_idx ON public.hat_defs USING btree (submitter_id);


--
-- Name: lowercase_original_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX lowercase_original_username ON public.users USING btree (lower((original_username)::text));


--
-- Name: lowercase_prelock_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX lowercase_prelock_username ON public.users USING btree (lower((prelock_username)::text));


--
-- Name: lowercase_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX lowercase_username ON public.users USING btree (lower((username)::text));


--
-- Name: modaction_action_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX modaction_action_idx ON public.modactions USING btree (kind);


--
-- Name: modaction_cid_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX modaction_cid_idx ON public.modactions USING btree (target_comment_id);


--
-- Name: modaction_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX modaction_id_idx ON public.modactions USING btree (id DESC);


--
-- Name: modaction_pid_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX modaction_pid_idx ON public.modactions USING btree (target_post_id);


--
-- Name: notifications_comment_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifications_comment_idx ON public.notifications USING btree (comment_id);


--
-- Name: notifs_user_read_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifs_user_read_idx ON public.notifications USING btree (user_id, read);


--
-- Name: option_comment; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX option_comment ON public.comment_options USING btree (parent_id);


--
-- Name: option_post; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX option_post ON public.post_options USING btree (parent_id);


--
-- Name: post_app_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX post_app_id_idx ON public.posts USING btree (app_id);


--
-- Name: post_author_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX post_author_id_idx ON public.posts USING btree (author_id);


--
-- Name: post_created_utc_asc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX post_created_utc_asc_idx ON public.posts USING btree (created_utc NULLS FIRST);


--
-- Name: post_created_utc_desc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX post_created_utc_desc_idx ON public.posts USING btree (created_utc DESC);


--
-- Name: post_deleted_utc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX post_deleted_utc_idx ON public.posts USING btree (deleted_utc);


--
-- Name: post_is_pinned_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX post_is_pinned_idx ON public.posts USING btree (is_pinned);


--
-- Name: post_new_sort_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX post_new_sort_idx ON public.posts USING btree (is_banned, deleted_utc, created_utc DESC, over_18);


--
-- Name: post_over_18_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX post_over_18_idx ON public.posts USING btree (over_18);


--
-- Name: posts_bump_utc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posts_bump_utc_idx ON public.posts USING btree (bump_utc);


--
-- Name: posts_stickied_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posts_stickied_idx ON public.posts USING btree (stickied);


--
-- Name: report_user_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX report_user_idx ON public.reports USING btree (user_id);


--
-- Name: subimssion_binary_group_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX subimssion_binary_group_idx ON public.posts USING btree (is_banned, deleted_utc, over_18);


--
-- Name: subscription_user_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX subscription_user_index ON public.subscriptions USING btree (user_id);


--
-- Name: transactions_email_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX transactions_email_idx ON public.transactions USING btree (email);


--
-- Name: user_private_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX user_private_idx ON public.users USING btree (is_private);


--
-- Name: users_bird_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_bird_idx ON public.users USING btree (bird);


--
-- Name: users_bite_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_bite_idx ON public.users USING btree (bite);


--
-- Name: users_chud_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_chud_idx ON public.users USING btree (chud);


--
-- Name: users_coins_spent_on_hats_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_coins_spent_on_hats_idx ON public.users USING btree (coins_spent_on_hats);


--
-- Name: users_created_utc_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_created_utc_index ON public.users USING btree (created_utc);


--
-- Name: users_deflector_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_deflector_idx ON public.users USING btree (deflector);


--
-- Name: users_earlylife_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_earlylife_idx ON public.users USING btree (earlylife);


--
-- Name: users_edgified_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_edgified_idx ON public.users USING btree (sharpen);


--
-- Name: users_flairchanged_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_flairchanged_idx ON public.users USING btree (flairchanged);


--
-- Name: users_longpost_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_longpost_idx ON public.users USING btree (longpost);


--
-- Name: users_marseyawarded_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_marseyawarded_idx ON public.users USING btree (marseyawarded);


--
-- Name: users_marsify_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_marsify_idx ON public.users USING btree (marsify);


--
-- Name: users_namechanged_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_namechanged_idx ON public.users USING btree (namechanged);


--
-- Name: users_original_username_trgm_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_original_username_trgm_idx ON public.users USING gin (original_username public.gin_trgm_ops);


--
-- Name: users_owoify_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_owoify_idx ON public.users USING btree (owoify);


--
-- Name: users_patron_utc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_patron_utc_idx ON public.users USING btree (patron_utc);


--
-- Name: users_prelock_username_trgm_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_prelock_username_trgm_idx ON public.users USING gin (prelock_username public.gin_trgm_ops);


--
-- Name: users_progressivestack_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_progressivestack_idx ON public.users USING btree (progressivestack);


--
-- Name: users_queen_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_queen_idx ON public.users USING btree (queen);


--
-- Name: users_rainbow_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_rainbow_idx ON public.users USING btree (rainbow);


--
-- Name: users_rehab_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_rehab_idx ON public.users USING btree (rehab);


--
-- Name: users_spider_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_spider_idx ON public.users USING btree (spider);


--
-- Name: users_subs_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_subs_idx ON public.users USING btree (stored_subscriber_count);


--
-- Name: users_unbanutc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_unbanutc_idx ON public.users USING btree (unban_utc DESC);


--
-- Name: users_username_trgm_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_username_trgm_idx ON public.users USING gin (username public.gin_trgm_ops);


--
-- Name: vote_user_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vote_user_index ON public.votes USING btree (user_id);


--
-- Name: votes_type_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX votes_type_index ON public.votes USING btree (vote_type);


--
-- Name: alts alt_user1_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alts
    ADD CONSTRAINT alt_user1_fkey FOREIGN KEY (user1) REFERENCES public.users(id);


--
-- Name: alts alt_user2_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alts
    ADD CONSTRAINT alt_user2_fkey FOREIGN KEY (user2) REFERENCES public.users(id);


--
-- Name: oauth_apps app_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oauth_apps
    ADD CONSTRAINT app_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: award_relationships award_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_comment_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id);


--
-- Name: award_relationships award_post_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_post_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: award_relationships award_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: badges badges_badge_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badges
    ADD CONSTRAINT badges_badge_id_fkey FOREIGN KEY (badge_id) REFERENCES public.badge_defs(id);


--
-- Name: badges badges_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badges
    ADD CONSTRAINT badges_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: userblocks block_target_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.userblocks
    ADD CONSTRAINT block_target_fkey FOREIGN KEY (target_id) REFERENCES public.users(id);


--
-- Name: userblocks block_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.userblocks
    ADD CONSTRAINT block_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: comments casino_game_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT casino_game_fkey FOREIGN KEY (casino_game_id) REFERENCES public.casino_games(id);


--
-- Name: casino_games casino_games_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.casino_games
    ADD CONSTRAINT casino_games_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: client_auths client_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_auths
    ADD CONSTRAINT client_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: comments comment_approver_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comment_approver_fkey FOREIGN KEY (is_approved) REFERENCES public.users(id);


--
-- Name: comments comment_parent_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comment_parent_comment_fkey FOREIGN KEY (parent_comment_id) REFERENCES public.comments(id);


--
-- Name: comments comment_parent_post_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comment_parent_post_fkey FOREIGN KEY (parent_post) REFERENCES public.posts(id);


--
-- Name: comment_save_relationship comment_save_relationship_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_save_relationship
    ADD CONSTRAINT comment_save_relationship_comment_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) MATCH FULL;


--
-- Name: comment_save_relationship comment_save_relationship_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_save_relationship
    ADD CONSTRAINT comment_save_relationship_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: comments comment_sentto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comment_sentto_fkey FOREIGN KEY (sentto) REFERENCES public.users(id);


--
-- Name: commentreports commentreports_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentreports
    ADD CONSTRAINT commentreports_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id);


--
-- Name: commentreports commentreports_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentreports
    ADD CONSTRAINT commentreports_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: comments comments_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: commentvotes commentvote_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentvotes
    ADD CONSTRAINT commentvote_comment_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) MATCH FULL;


--
-- Name: commentvotes commentvote_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentvotes
    ADD CONSTRAINT commentvote_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: emojis emoji_author_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emojis
    ADD CONSTRAINT emoji_author_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: emojis emoji_submitter_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emojis
    ADD CONSTRAINT emoji_submitter_fkey FOREIGN KEY (submitter_id) REFERENCES public.users(id);


--
-- Name: exiles exile_exiler_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exiles
    ADD CONSTRAINT exile_exiler_fkey FOREIGN KEY (exiler_id) REFERENCES public.users(id);


--
-- Name: exiles exile_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exiles
    ADD CONSTRAINT exile_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name);


--
-- Name: exiles exile_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exiles
    ADD CONSTRAINT exile_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: lotteries fk_winner; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lotteries
    ADD CONSTRAINT fk_winner FOREIGN KEY (winner_id) REFERENCES public.users(id);


--
-- Name: follows follow_target_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follows
    ADD CONSTRAINT follow_target_fkey FOREIGN KEY (target_id) REFERENCES public.users(id);


--
-- Name: follows follow_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follows
    ADD CONSTRAINT follow_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: group_memberships group_memberships_group_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_group_fkey FOREIGN KEY (group_name) REFERENCES public.groups(name);


--
-- Name: group_memberships group_memberships_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: hat_defs hat_def_submitter_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hat_defs
    ADD CONSTRAINT hat_def_submitter_fkey FOREIGN KEY (submitter_id) REFERENCES public.users(id);


--
-- Name: hat_defs hat_defs_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hat_defs
    ADD CONSTRAINT hat_defs_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: hats hats_hat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hats
    ADD CONSTRAINT hats_hat_id_fkey FOREIGN KEY (hat_id) REFERENCES public.hat_defs(id);


--
-- Name: hats hats_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hats
    ADD CONSTRAINT hats_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: media media_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media
    ADD CONSTRAINT media_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: mods mod_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mods
    ADD CONSTRAINT mod_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name);


--
-- Name: modactions modactions_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modactions
    ADD CONSTRAINT modactions_comment_fkey FOREIGN KEY (target_comment_id) REFERENCES public.comments(id);


--
-- Name: modactions modactions_post_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modactions
    ADD CONSTRAINT modactions_post_fkey FOREIGN KEY (target_post_id) REFERENCES public.posts(id);


--
-- Name: modactions modactions_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modactions
    ADD CONSTRAINT modactions_user_fkey FOREIGN KEY (target_user_id) REFERENCES public.users(id);


--
-- Name: notifications notifications_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: client_auths oauth_client_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_auths
    ADD CONSTRAINT oauth_client_fkey FOREIGN KEY (oauth_client) REFERENCES public.oauth_apps(id);


--
-- Name: comment_options option_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_options
    ADD CONSTRAINT option_comment_fkey FOREIGN KEY (parent_id) REFERENCES public.comments(id) MATCH FULL;


--
-- Name: post_options option_post_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_options
    ADD CONSTRAINT option_post_fkey FOREIGN KEY (parent_id) REFERENCES public.posts(id) MATCH FULL;


--
-- Name: posts post_approver_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT post_approver_fkey FOREIGN KEY (is_approved) REFERENCES public.users(id);


--
-- Name: posts post_author_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT post_author_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: push_subscriptions push_subscriptions_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_subscriptions
    ADD CONSTRAINT push_subscriptions_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: reports reports_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: reports reports_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: save_relationship save_relationship_post_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.save_relationship
    ADD CONSTRAINT save_relationship_post_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id) MATCH FULL;


--
-- Name: save_relationship save_relationship_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.save_relationship
    ADD CONSTRAINT save_relationship_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: comments stickied_child_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT stickied_child_fkey FOREIGN KEY (stickied_child_id) REFERENCES public.comments(id);


--
-- Name: sub_blocks sub_blocks_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_blocks
    ADD CONSTRAINT sub_blocks_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name) MATCH FULL;


--
-- Name: sub_blocks sub_blocks_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_blocks
    ADD CONSTRAINT sub_blocks_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: posts sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name);


--
-- Name: sub_joins sub_joins_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_joins
    ADD CONSTRAINT sub_joins_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name) MATCH FULL;


--
-- Name: sub_joins sub_joins_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_joins
    ADD CONSTRAINT sub_joins_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: sub_subscriptions sub_subscriptions_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_subscriptions
    ADD CONSTRAINT sub_subscriptions_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name) MATCH FULL;


--
-- Name: sub_subscriptions sub_subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_subscriptions
    ADD CONSTRAINT sub_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: subactions subactions_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subactions
    ADD CONSTRAINT subactions_comment_fkey FOREIGN KEY (target_comment_id) REFERENCES public.comments(id);


--
-- Name: subactions subactions_post_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subactions
    ADD CONSTRAINT subactions_post_fkey FOREIGN KEY (target_post_id) REFERENCES public.posts(id);


--
-- Name: subactions subactions_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subactions
    ADD CONSTRAINT subactions_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name);


--
-- Name: subactions subactions_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subactions
    ADD CONSTRAINT subactions_user_fkey FOREIGN KEY (target_user_id) REFERENCES public.users(id);


--
-- Name: subscriptions subscription_post_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscription_post_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: subscriptions subscription_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscription_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users user_blacklisted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT user_blacklisted_by_fkey FOREIGN KEY (blacklisted_by) REFERENCES public.users(id);


--
-- Name: users user_chudded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT user_chudded_by_fkey FOREIGN KEY (chudded_by) REFERENCES public.users(id);


--
-- Name: users user_is_banned_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT user_is_banned_fkey FOREIGN KEY (is_banned) REFERENCES public.users(id);


--
-- Name: mods user_mod_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mods
    ADD CONSTRAINT user_mod_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users user_referrer_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT user_referrer_fkey FOREIGN KEY (referred_by) REFERENCES public.users(id);


--
-- Name: users user_shadowbanned_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT user_shadowbanned_fkey FOREIGN KEY (shadowbanned) REFERENCES public.users(id);


--
-- Name: viewers view_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.viewers
    ADD CONSTRAINT view_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: viewers view_viewer_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.viewers
    ADD CONSTRAINT view_viewer_fkey FOREIGN KEY (viewer_id) REFERENCES public.users(id);


--
-- Name: comment_option_votes vote_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_option_votes
    ADD CONSTRAINT vote_comment_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) MATCH FULL;


--
-- Name: post_option_votes vote_option_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_option_votes
    ADD CONSTRAINT vote_option_fkey FOREIGN KEY (option_id) REFERENCES public.post_options(id) MATCH FULL;


--
-- Name: comment_option_votes vote_option_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_option_votes
    ADD CONSTRAINT vote_option_fkey FOREIGN KEY (option_id) REFERENCES public.comment_options(id) MATCH FULL;


--
-- Name: post_option_votes vote_post_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_option_votes
    ADD CONSTRAINT vote_post_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id) MATCH FULL;


--
-- Name: votes vote_post_key; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT vote_post_key FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: votes vote_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT vote_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: post_option_votes vote_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_option_votes
    ADD CONSTRAINT vote_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: comment_option_votes vote_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_option_votes
    ADD CONSTRAINT vote_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: comments wall_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT wall_user_id_fkey FOREIGN KEY (wall_user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

