from django.shortcuts import render


def example(request):
    document_id = request.GET.get('id')
    return render(request, 'Websocket-example.html', {"document_id": document_id})
