--
-- PostgreSQL database dump
--

\restrict lmmrFpSnZmzkMQUoGlhaYomc82ZqY2MTAWqTRZETzs8dG5aGQIxF7ihIHyWtIBX

-- Dumped from database version 16.11 (Homebrew)
-- Dumped by pg_dump version 16.11 (Homebrew)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: vincentlaurent
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO vincentlaurent;

--
-- Name: check_ins; Type: TABLE; Schema: public; Owner: vincentlaurent
--

CREATE TABLE public.check_ins (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    goal_id uuid,
    message_sent text NOT NULL,
    check_in_type character varying(50) NOT NULL,
    sent_at timestamp with time zone DEFAULT now() NOT NULL,
    responded boolean NOT NULL,
    responded_at timestamp with time zone
);


ALTER TABLE public.check_ins OWNER TO vincentlaurent;

--
-- Name: conversations; Type: TABLE; Schema: public; Owner: vincentlaurent
--

CREATE TABLE public.conversations (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    title character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.conversations OWNER TO vincentlaurent;

--
-- Name: daily_logs; Type: TABLE; Schema: public; Owner: vincentlaurent
--

CREATE TABLE public.daily_logs (
    id uuid NOT NULL,
    goal_id uuid NOT NULL,
    user_id uuid NOT NULL,
    log_date date NOT NULL,
    weight double precision,
    meals_rating character varying(50),
    hunger_awareness character varying(50),
    emotional_eating boolean,
    emotion_if_eating character varying(100),
    mood character varying(50),
    energy character varying(50),
    notes text,
    data jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.daily_logs OWNER TO vincentlaurent;

--
-- Name: goals; Type: TABLE; Schema: public; Owner: vincentlaurent
--

CREATE TABLE public.goals (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    category character varying(100) NOT NULL,
    status character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    start_date date,
    target_date date,
    settings jsonb,
    metrics jsonb,
    milestones_achieved jsonb,
    current_streak integer NOT NULL,
    best_streak integer NOT NULL
);


ALTER TABLE public.goals OWNER TO vincentlaurent;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: vincentlaurent
--

CREATE TABLE public.messages (
    id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    role character varying(20) NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.messages OWNER TO vincentlaurent;

--
-- Name: progress_entries; Type: TABLE; Schema: public; Owner: vincentlaurent
--

CREATE TABLE public.progress_entries (
    id uuid NOT NULL,
    goal_id uuid NOT NULL,
    note text,
    mood character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.progress_entries OWNER TO vincentlaurent;

--
-- Name: user_engagement; Type: TABLE; Schema: public; Owner: vincentlaurent
--

CREATE TABLE public.user_engagement (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    unanswered_checkins integer NOT NULL,
    total_checkins_sent integer NOT NULL,
    total_responses integer NOT NULL,
    last_checkin_sent timestamp with time zone,
    last_user_message timestamp with time zone,
    paused boolean NOT NULL,
    paused_at timestamp with time zone,
    preferred_check_in_times jsonb,
    night_start_hour integer NOT NULL,
    night_end_hour integer NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_engagement OWNER TO vincentlaurent;

--
-- Name: users; Type: TABLE; Schema: public; Owner: vincentlaurent
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(255),
    name character varying(255),
    picture character varying(500),
    oauth_provider character varying(50) NOT NULL,
    oauth_id character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    locale character varying(10),
    timezone integer,
    gender character varying(20)
);


ALTER TABLE public.users OWNER TO vincentlaurent;

--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: check_ins check_ins_pkey; Type: CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.check_ins
    ADD CONSTRAINT check_ins_pkey PRIMARY KEY (id);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: daily_logs daily_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.daily_logs
    ADD CONSTRAINT daily_logs_pkey PRIMARY KEY (id);


--
-- Name: goals goals_pkey; Type: CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.goals
    ADD CONSTRAINT goals_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: progress_entries progress_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.progress_entries
    ADD CONSTRAINT progress_entries_pkey PRIMARY KEY (id);


--
-- Name: user_engagement user_engagement_pkey; Type: CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.user_engagement
    ADD CONSTRAINT user_engagement_pkey PRIMARY KEY (id);


--
-- Name: user_engagement user_engagement_user_id_key; Type: CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.user_engagement
    ADD CONSTRAINT user_engagement_user_id_key UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: vincentlaurent
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: check_ins check_ins_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.check_ins
    ADD CONSTRAINT check_ins_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goals(id);


--
-- Name: check_ins check_ins_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.check_ins
    ADD CONSTRAINT check_ins_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: conversations conversations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: daily_logs daily_logs_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.daily_logs
    ADD CONSTRAINT daily_logs_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goals(id);


--
-- Name: daily_logs daily_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.daily_logs
    ADD CONSTRAINT daily_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: goals goals_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.goals
    ADD CONSTRAINT goals_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: messages messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id);


--
-- Name: progress_entries progress_entries_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.progress_entries
    ADD CONSTRAINT progress_entries_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goals(id);


--
-- Name: user_engagement user_engagement_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vincentlaurent
--

ALTER TABLE ONLY public.user_engagement
    ADD CONSTRAINT user_engagement_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict lmmrFpSnZmzkMQUoGlhaYomc82ZqY2MTAWqTRZETzs8dG5aGQIxF7ihIHyWtIBX

