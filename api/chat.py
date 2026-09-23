from flask import Blueprint, request, jsonify, Response, stream_with_context
from memory.store import memory
import json
import time

bp = Blueprint('chat', __name__)


def register(gemma, rag, web_search, weather_get):

    def fast_plan(q, city):
        lower = q.lower()

        crops = [
            "tomato", "wheat", "rice", "potato",
            "maize", "corn", "cotton", "mustard",
            "sugarcane", "onion", "chilli", "pea",
            "soybean", "groundnut", "okra", "brinjal"
        ]

        agriculture_terms = [
            "crop", "plant", "farm", "farmer",
            "soil", "seed", "sowing", "harvest",
            "fertilizer", "fertiliser", "manure",
            "irrigation", "irrigate", "watering",
            "water", "pest", "disease", "weed",
            "cultivation", "agriculture", "agricultural",
            "yield"
        ]

        subject = next(
            (crop for crop in crops if crop in lower),
            ""
        )

        is_agriculture = (
            bool(subject)
            or any(term in lower for term in agriculture_terms)
        )

        # Weather is only needed for explicitly weather-dependent questions.
        weather_terms = [
            "today",
            "tomorrow",
            "weather",
            "rain",
            "rainfall",
            "temperature",
            "humidity",
            "forecast",
            "wind"
        ]

        weather_required = bool(
            city
            and is_agriculture
            and any(term in lower for term in weather_terms)
        )

        irrigation_terms = [
            "water",
            "watering",
            "irrigat",
            "moisture"
        ]

        if subject and any(term in lower for term in irrigation_terms):
            queries = [
                f"{subject} irrigation watering requirements",
                f"{subject} water stress"
            ]

            intent = "irrigation"
            task = "determine watering requirements"

        else:
            queries = [q]
            intent = (
                "general_agriculture"
                if is_agriculture
                else "general"
            )
            task = q

        return {
            "intent": intent,
            "subject": subject,
            "task": task,
            "weather_required": weather_required,
            "queries": queries,
            "agriculture": is_agriculture
        }


    def compact_weather(weather):
        if not weather:
            return None

        try:
            current = weather["forecast"]["current"]

            return {
                "location": weather["location"]["name"],
                "temperature_c": current["temperature_2m"],
                "humidity_percent": current["relative_humidity_2m"],
                "precipitation_mm": current["precipitation"],
                "wind_kmh": current["wind_speed_10m"],
                "time": current["time"]
            }

        except Exception:
            return None


    def prepare_chat(d):

        start = time.time()

        q = (d.get('message') or '').strip()
        city = (d.get('city') or '').strip()

        if not q:
            return None, jsonify({
                'error': 'message is required'
            }), 400

        cid = memory.ensure(
            d.get('conversation_id')
        )

        history = memory.get(cid)

        plan = fast_plan(q, city)

        evidence = []

        if plan["agriculture"]:

            queries = plan.get(
                'queries'
            ) or [q]

            for x in queries[:2]:

                evidence.extend(
                    rag.search(x, 2)
                )

                if web_search:
                    evidence.extend(
                        web_search(x)
                    )

        seen = set()
        unique = []

        for e in sorted(
            evidence,
            key=lambda x: x.get('score', 0),
            reverse=True
        ):

            key = (
                e.get('source'),
                e.get('page'),
                e.get('url'),
                e.get('text', '')[:100]
            )

            if key not in seen:
                seen.add(key)
                unique.append(e)

        evidence = unique[:2]

        weather = None

        if plan.get('weather_required', False):

            try:
                weather = weather_get(city)

            except Exception as e:

                print('[Weather] error:', e)

                weather = {
                    'error': str(e)
                }

        compact = compact_weather(weather)

        # Keep only the most recent two conversation messages.
        recent_history = history[-2:]

        hist = '\n'.join(
            f"{x['role']}: {x['content']}"
            for x in recent_history
        )

        if not hist:
            hist = '(none)'

        # Keep retrieved evidence short.
        evidence_blocks = []

        for i, e in enumerate(evidence):

            text = e.get('text', '').strip()

            # Hard limit for each evidence chunk.
            text = text[:900]

            evidence_blocks.append(
                f"[{i + 1}] "
                f"{e.get('source', 'unknown')}"
                f" page {e.get('page', '')}\n"
                f"{text}"
            )

        ev = '\n\n'.join(evidence_blocks)

        if not ev:
            ev = '(No retrieved evidence.)'

        weather_text = (
            json.dumps(compact, ensure_ascii=False)
            if compact
            else '(not available)'
        )

        prompt = f"""Question:
{q}

City:
{city or '(none)'}

Conversation:
{hist}

Weather:
{weather_text}

Evidence:
{ev}

Answer the question using the evidence.
Use weather only when relevant to the question.
Do not infer that weather means watering is required.
Do not invent facts.
Cite supplied evidence as [1] or [2].
Keep the answer concise, under 80 words."""

        elapsed = time.time() - start

        print(
            f"[TIMING] prepare_chat done: "
            f"{elapsed:.2f} sec"
        )

        print(
            f"[TIMING] prompt characters: "
            f"{len(prompt)}"
        )

        return {
            'q': q,
            'city': city,
            'cid': cid,
            'plan': plan,
            'weather': weather,
            'compact_weather': compact,
            'evidence': evidence,
            'prompt': prompt
        }, None, None


    @bp.post('/api/chat')
    def chat():

        start = time.time()

        d = request.get_json(
            silent=True
        ) or {}

        data, error, status = prepare_chat(d)

        if error:
            return error, status

        print(
            "[TIMING] starting gemma.generate"
        )

        answer = gemma.generate(
            data['prompt'],
            max_tokens=100,
            temperature=0.2
        )

        print(
            f"[TIMING] gemma.generate: "
            f"{time.time() - start:.2f} sec"
        )

        memory.add(
            data['cid'],
            'user',
            data['q']
        )

        memory.add(
            data['cid'],
            'assistant',
            answer
        )

        print(
            f"[TIMING] total request: "
            f"{time.time() - start:.2f} sec"
        )

        return jsonify({
            'conversation_id': data['cid'],
            'answer': answer,
            'plan': data['plan'],
            'weather': data['weather'],
            'sources': [
                {
                    k: e[k]
                    for k in (
                        'source',
                        'url',
                        'page',
                        'score',
                        'type'
                    )
                    if k in e
                }
                for e in data['evidence']
            ]
        })


    @bp.post('/api/chat/stream')
    def chat_stream():

        start = time.time()

        d = request.get_json(
            silent=True
        ) or {}

        data, error, status = prepare_chat(d)

        if error:
            return error, status

        @stream_with_context
        def generate():

            full_answer = []

            yield json.dumps({
                'type': 'meta',
                'conversation_id': data['cid'],
                'plan': data['plan'],
                'weather': data['weather'],
                'sources': [
                    {
                        k: e[k]
                        for k in (
                            'source',
                            'url',
                            'page',
                            'score',
                            'type'
                        )
                        if k in e
                    }
                    for e in data['evidence']
                ]
            }, ensure_ascii=False) + '\n'

            print(
                f"[TIMING] stream: "
                f"starting Gemma: "
                f"{time.time() - start:.2f} sec"
            )

            first_token = True

            try:

                for text in gemma.stream(
                    data['prompt'],
                    max_tokens=100,
                    temperature=0.2
                ):

                    if first_token:

                        print(
                            f"[TIMING] FIRST TOKEN: "
                            f"{time.time() - start:.2f} sec"
                        )

                        first_token = False

                    full_answer.append(text)

                    yield json.dumps({
                        'type': 'token',
                        'text': text
                    }, ensure_ascii=False) + '\n'

                answer = ''.join(
                    full_answer
                ).strip()

                memory.add(
                    data['cid'],
                    'user',
                    data['q']
                )

                memory.add(
                    data['cid'],
                    'assistant',
                    answer
                )

                print(
                    f"[TIMING] Gemma stream finished: "
                    f"{time.time() - start:.2f} sec"
                )

                yield json.dumps({
                    'type': 'done'
                }) + '\n'

                print(
                    f"[TIMING] TOTAL STREAM REQUEST: "
                    f"{time.time() - start:.2f} sec"
                )

            except Exception as e:

                print(
                    '[Gemma stream] error:',
                    e
                )

                yield json.dumps({
                    'type': 'error',
                    'message': str(e)
                }) + '\n'

        return Response(
            generate(),
            mimetype='application/x-ndjson'
        )


    return bp